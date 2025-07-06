"""
Research Engine - 調査実行エンジン
"""
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from src.engine.web_search import WebSearchInterface

# ロギング設定
logger = logging.getLogger(__name__)


class WebSearchProtocol(Protocol):
    """Web Search のプロトコル定義"""

    def search_multiple(self, queries: List[str]) -> List[Dict[str, Any]]:
        ...


@dataclass
class EngineConfig:
    """エンジン設定のデータクラス"""

    max_prompt_length: int = 8000
    web_search_enabled: bool = True
    max_search_queries: int = 5
    search_timeout: int = 30
    result_timeout: int = 300


class ResearchEngine:
    def __init__(
        self,
        web_search: Optional[WebSearchProtocol] = None,
        config: Optional[EngineConfig] = None,
    ) -> None:
        """依存性注入による初期化"""
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.web_search = web_search or WebSearchInterface()
        self.config = config or EngineConfig()
        self.prompts_dir = self.root_dir / "prompts"

    def execute_research(
        self,
        config_data: Dict[str, Any],
        phase_name: str,
        theme_id: str,
        step: int,
        previous_results: Optional[Dict[str, Any]] = None,
        theme_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """調査の実行"""
        start_time = time.time()

        try:
            # プロンプトの読み込み
            prompt = self.load_prompt(phase_name, theme_id, step)

            # 変数の置換
            prompt = self.replace_variables(prompt, config_data)

            # 前の結果を含める
            if step > 1 and theme_results:
                prompt = self.add_previous_context(prompt, theme_results)

            if previous_results and step == 1:
                prompt = self.add_phase_context(prompt, previous_results)

            # プロンプト長のチェック
            if len(prompt) > self.config.max_prompt_length:
                logger.warning(f"プロンプトが長すぎます ({len(prompt)}文字)。要約版を使用します。")
                prompt = self._truncate_prompt(prompt)

            # Cursor AIに調査を実行させる
            logger.info(f"\n🔍 以下のプロンプトで調査を実行します:")
            logger.info("-" * 80)
            logger.info(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            logger.info("-" * 80)

            # ここでCursor AIのAuto機能を使用
            research_result = self.execute_with_cursor_ai(prompt)

            # Web検索で情報を補強
            if config_data.get("enable_web_search", self.config.web_search_enabled):
                try:
                    search_queries = self.extract_search_queries(research_result)
                    if search_queries:
                        web_results = self.web_search.search_multiple(
                            search_queries[: self.config.max_search_queries]
                        )
                        research_result = self.enhance_with_web_results(
                            research_result, web_results
                        )
                except Exception as e:
                    logger.warning(f"Web検索の補強中にエラーが発生: {e}")

            execution_time = time.time() - start_time
            logger.info(f"調査実行完了 (所要時間: {execution_time:.1f}秒)")

            return {
                "theme_id": theme_id,
                "step": step,
                "prompt": prompt,
                "result": research_result,
                "timestamp": datetime.now().isoformat(),
                "sources": self.extract_sources(research_result),
                "execution_time": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"調査実行中にエラーが発生: {e}")
            return {
                "theme_id": theme_id,
                "step": step,
                "prompt": prompt if "prompt" in locals() else "",
                "result": f"エラーが発生しました: {e}",
                "timestamp": datetime.now().isoformat(),
                "sources": [],
                "execution_time": execution_time,
                "error": str(e),
            }

    def _truncate_prompt(self, prompt: str) -> str:
        """プロンプトを適切な長さに切り詰める"""
        lines = prompt.split("\n")
        truncated_lines = []
        current_length = 0

        for line in lines:
            if current_length + len(line) > self.config.max_prompt_length - 200:
                truncated_lines.append("\n... (プロンプトが長すぎるため省略)")
                break
            truncated_lines.append(line)
            current_length += len(line) + 1

        return "\n".join(truncated_lines)

    def load_prompt(self, phase_name: str, theme_id: str, step: int) -> str:
        """プロンプトファイルの読み込み"""
        prompt_file = self.prompts_dir / phase_name / f"{theme_id}_step{step}.md"

        if not prompt_file.exists():
            # デフォルトプロンプトを生成
            return self.generate_default_prompt(phase_name, theme_id, step)

        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError as e:
            logger.error(f"プロンプトファイルが見つかりません: {prompt_file}")
            return self.generate_default_prompt(phase_name, theme_id, step)
        except Exception as e:
            logger.error(f"プロンプトファイルの読み込みに失敗: {e}")
            return self.generate_default_prompt(phase_name, theme_id, step)

    def generate_default_prompt(self, phase_name: str, theme_id: str, step: int) -> str:
        """デフォルトプロンプトの生成"""
        prompts_map = {
            "step1": """# 命令書：フェーズ{phase} - {theme} - 現状分析

あなたは、{role}です。
{company}の{theme}について、以下の観点から現状を分析してください：

1. 現状の把握と課題の特定
2. 業界ベストプラクティスとの比較
3. 定量的・定性的データの収集と分析

必ず以下を含めてください：
- 最低10個以上の信頼できる情報源からの引用
- 具体的な数値やデータ
- 視覚的な図表（可能な場合）

Web検索を活用して最新の情報を収集し、深い分析を行ってください。
""",
            "step2": """# 命令書：フェーズ{phase} - {theme} - 戦略立案

前のステップの分析結果を踏まえ、以下を策定してください：

1. 戦略オプションの検討（最低3案）
2. 各オプションの評価（メリット・デメリット・実現可能性）
3. 推奨戦略の選定と根拠

参照すべき前の分析結果：
{previous_context}

必ず根拠となるデータや事例を示してください。
""",
            "step3": """# 命令書：フェーズ{phase} - {theme} - 実行計画

選定された戦略を実現するための具体的な実行計画を策定してください：

1. アクションプランの詳細（タスク・担当・期限）
2. 必要なリソース（人材・予算・ツール）
3. KPIと成功指標の設定
4. リスクと対策

実行可能性を重視し、具体的で測定可能な計画を作成してください。
""",
        }

        step_key = f"step{step}"
        template = prompts_map.get(step_key, prompts_map["step1"])

        return template.format(
            phase=phase_name,
            theme=theme_id,
            role=self.get_role_for_theme(theme_id),
            company="{company}",  # 後で置換
        )

    def replace_variables(self, prompt: str, config_data: Dict[str, Any]) -> str:
        """PDFで定義されたすべての変数を置換"""
        # 基本変数
        replacements = {
            "[自社名]": config_data.get("company_name", ""),
            "[業界]": config_data.get("industry", ""),
            "[主要製品/サービス]": config_data.get("product_service", ""),
            "[製品/サービス]": config_data.get("product_service", ""),
            "[自社製品/サービス]": config_data.get("product_service", ""),
            "[製品/サービス名]": config_data.get("product_service", ""),
            "[対象市場]": config_data.get("target_market", ""),
            "[市場]": config_data.get("target_market", ""),
            "[ターゲット市場]": config_data.get("target_market", ""),
            "[国・地域]": config_data.get("region", ""),
            "[競合企業]": ", ".join(config_data.get("competitors", [])),
            "[競合]": ", ".join(config_data.get("competitors", [])),
            "[ターゲット顧客]": config_data.get("target_customer", ""),
            "[分析対象とする主要な顧客ペルソナ]": config_data.get("persona", ""),
            "[新機能や新製品のアイデア]": config_data.get("new_product_idea", ""),
            "[想定するターゲットユーザー]": config_data.get("target_user", ""),
            "[候補国]": config_data.get("candidate_countries", ""),
            "[ブランド名]": config_data.get(
                "brand_name", config_data.get("company_name", "")
            ),
            "[自社/事業部]": config_data.get(
                "division", config_data.get("company_name", "")
            ),
            "[計測可能な最重要目標]": config_data.get("main_goal", ""),
            "[総予算額]": config_data.get("budget", ""),
            "[キャンペーン目的]": config_data.get("campaign_objective", ""),
            "[テーマ]": config_data.get("theme", ""),
            "[目的]": config_data.get("objective", ""),
        }

        for key, value in replacements.items():
            prompt = prompt.replace(key, value)

        return prompt

    def execute_with_cursor_ai(self, prompt: str) -> str:
        """Cursor AIでの実行（対話的実行）"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 以下の内容をCursorのチャット欄にコピーして実行してください：")
        logger.info("=" * 80)

        cursor_prompt = f"""
{prompt}

【重要な指示】
1. 必ずWeb検索を積極的に活用して、2024年の最新情報を収集してください
2. 最低10個以上の信頼できる情報源を引用してください
3. 具体的な数値データを含めてください
4. 可能な限り図表を作成してください（テキストベースでOK）

出力は必ずマークダウン形式で、以下の構造にしてください：
- 明確な見出し（#, ##, ###）
- 箇条書き（-, *）
- 表形式のデータ（|表|形式|）
- 引用元の明記 [1], [2]...

調査完了後、結果全体をコピーして返してください。
"""

        print(cursor_prompt)
        print("\n" + "=" * 80)
        print("📝 調査結果を入力してください（Ctrl+Dで完了）:")

        # ユーザーからの入力を待機
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        result = "\n".join(lines)

        if not result.strip():
            logger.warning("調査結果が空です。デフォルトの結果を返します。")
            return "調査結果が入力されませんでした。"

        return result

    def extract_search_queries(self, research_result: str) -> List[str]:
        """調査結果から検索クエリを抽出"""
        queries = []

        # 基本的なキーワード抽出
        lines = research_result.split("\n")
        for line in lines:
            if any(
                keyword in line.lower() for keyword in ["市場", "競合", "トレンド", "統計", "分析"]
            ):
                # 行からキーワードを抽出
                words = line.split()
                if len(words) >= 2:
                    query = " ".join(words[:3])  # 最初の3単語を使用
                    queries.append(query)

        # 重複を除去
        unique_queries = list(set(queries))

        logger.info(f"抽出された検索クエリ: {unique_queries[:3]}...")
        return unique_queries

    def enhance_with_web_results(
        self, research_result: str, web_results: List[Dict[str, Any]]
    ) -> str:
        """Web検索結果で調査結果を補強"""
        if not web_results:
            return research_result

        enhancement = "\n\n## Web検索による補強情報\n\n"

        for i, result in enumerate(web_results[:5], 1):
            enhancement += f"### 補強情報 {i}\n"
            enhancement += f"**タイトル**: {result.get('title', 'N/A')}\n"
            enhancement += f"**要約**: {result.get('snippet', 'N/A')}\n"
            enhancement += f"**出典**: {result.get('url', 'N/A')}\n\n"

        return research_result + enhancement

    def extract_sources(self, research_result: str) -> List[str]:
        """調査結果から情報源を抽出"""
        sources = []

        # URLパターンを検索
        import re

        url_pattern = r"https?://[^\s\)]+"
        urls = re.findall(url_pattern, research_result)
        sources.extend(urls)

        # 引用パターンを検索
        citation_pattern = r"\[(\d+)\].*?(https?://[^\s\)]+)"
        citations = re.findall(citation_pattern, research_result)
        sources.extend([citation[1] for citation in citations])

        # 重複を除去
        unique_sources = list(set(sources))

        logger.info(f"抽出された情報源: {len(unique_sources)}件")
        return unique_sources

    def get_role_for_theme(self, theme_id: str) -> str:
        """テーマIDからロールを取得"""
        role_mapping = {
            "A": "マッキンゼー・アンド・カンパニーに所属する経営コンサルタント",
            "B": "BCG（ボストン・コンサルティング・グループ）の戦略コンサルタント",
            "1": "マッキンゼー・アンド・カンパニーの戦略コンサルタント",
            "2": "PwCの戦略コンサルタント",
            "3": "デロイトの競合分析専門家",
            "4": "アクセンチュアのテクノロジー戦略コンサルタント",
            "5": "EYの顧客分析専門家",
            "6": "KPMGのマーケティング戦略コンサルタント",
            "7": "ベイン・アンド・カンパニーの顧客体験専門家",
            "8": "ATカーニーのプロダクト戦略コンサルタント",
            "9": "ローランド・ベルガーのブランド戦略コンサルタント",
            "10": "サイモン・クッチャー・パートナーズのGTM戦略コンサルタント",
            "11": "A.T.カーニーのパートナーシップ戦略コンサルタント",
            "12": "マッキンゼーのグローバル戦略コンサルタント",
            "13": "BCGのグロース戦略コンサルタント",
            "14": "PwCの財務分析専門家",
            "15": "デロイトのフリーミアム戦略コンサルタント",
            "16": "アクセンチュアのマーケティング戦略コンサルタント",
            "17": "EYのクリエイティブ戦略コンサルタント",
            "18": "KPMGの広報戦略コンサルタント",
            "19": "ベインのメディアプランニング専門家",
            "20": "ATカーニーのYouTube戦略コンサルタント",
            "21": "ローランド・ベルガーのInstagram戦略コンサルタント",
            "22": "サイモン・クッチャーのTwitter戦略コンサルタント",
            "23": "マッキンゼーのTikTok戦略コンサルタント",
            "24": "BCGのアフィリエイト戦略コンサルタント",
            "25": "PwCのインフルエンサーマーケティングコンサルタント",
            "26": "デロイトのコミュニティ戦略コンサルタント",
            "27": "アクセンチュアのマーケティングテクノロジーコンサルタント",
            "28": "EYのセールス・イネーブルメントコンサルタント",
            "29": "KPMGのKPI設計コンサルタント",
            "30": "ベインの人材・予算戦略コンサルタント",
            "31": "ATカーニーのデータ駆動型意思決定コンサルタント",
            "32": "ローランド・ベルガーの組織変革コンサルタント",
            "33": "サイモン・クッチャーのESG戦略コンサルタント",
            "34": "マッキンゼーのリスクマネジメントコンサルタント",
            "35": "BCGのクライシス・マネジメントコンサルタント",
            "Z": "マッキンゼー・アンド・カンパニーのシニアパートナー",
        }

        return role_mapping.get(theme_id, "経営コンサルタント")

    def add_previous_context(
        self, prompt: str, theme_results: List[Dict[str, Any]]
    ) -> str:
        """前のステップの結果をコンテキストに追加"""
        if not theme_results:
            return prompt

        context = "\n\n## 前のステップの分析結果\n\n"

        for i, result in enumerate(theme_results, 1):
            context += f"### ステップ{i}の主要な発見\n"
            # 結果から主要なポイントを抽出
            result_text = result.get("result", "")
            lines = result_text.split("\n")
            key_points = []

            for line in lines:
                if any(keyword in line for keyword in ["重要", "結論", "推奨", "ポイント", "発見"]):
                    key_points.append(line.strip())
                    if len(key_points) >= 3:
                        break

            context += "\n".join(key_points) + "\n\n"

        return prompt + context

    def add_phase_context(self, prompt: str, previous_results: Dict[str, Any]) -> str:
        """前フェーズの結果をコンテキストに追加"""
        if not previous_results:
            return prompt

        context = "\n\n## 前フェーズの主要な分析結果\n\n"

        for phase_name, phase_data in previous_results.items():
            if isinstance(phase_data, dict) and "results" in phase_data:
                context += f"### {phase_name}の主要な発見\n"
                # フェーズの主要な結果を要約
                context += "- 前フェーズの分析結果を踏まえた戦略立案\n"
                context += "- 継続的な改善と最適化の実施\n\n"

        return prompt + context
