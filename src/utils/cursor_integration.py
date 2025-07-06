"""
Cursor Integration Helper - Cursor連携ヘルパー
"""
import logging
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime

# ロギング設定
logger = logging.getLogger(__name__)


class CursorIntegrationProtocol(Protocol):
    """Cursor統合のプロトコル定義"""

    def format_prompt_for_cursor(
        self, base_prompt: str, config_data: Dict[str, Any]
    ) -> str:
        ...


@dataclass
class CursorConfig:
    """Cursor統合設定のデータクラス"""

    max_prompt_length: int = 8000
    web_search_enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout_seconds: int = 300


class CursorIntegration:
    def __init__(self, config: Optional[CursorConfig] = None) -> None:
        """依存性注入による初期化"""
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.config = config or CursorConfig()
        self.temp_dir = self.root_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)

    def format_prompt_for_cursor(
        self, base_prompt: str, config_data: Dict[str, Any]
    ) -> str:
        """Cursor用にプロンプトをフォーマット"""
        try:
            web_search_instruction = """
【Web検索の活用方法】
1. 検索ボタンをクリックしてWeb検索を有効化
2. 以下のキーワードで検索：
   - {company_name} {industry} 市場分析 2024
   - {competitors} 戦略 事例
   - {target_market} トレンド 統計
3. 信頼できる情報源を優先（公式サイト、業界レポート、政府統計など）
""".format(
                company_name=config_data.get("company_name", ""),
                industry=config_data.get("industry", ""),
                competitors=", ".join(config_data.get("competitors", [])),
                target_market=config_data.get("target_market", ""),
            )

            cursor_prompt = f"""
# Cursor AI 調査プロンプト

## 基本情報
- **企業名**: {config_data.get('company_name', '')}
- **業界**: {config_data.get('industry', '')}
- **対象市場**: {config_data.get('target_market', '')}
- **競合企業**: {', '.join(config_data.get('competitors', []))}

## 調査指示

{base_prompt}

## Web検索活用ガイド

{web_search_instruction}

## 出力形式
- マークダウン形式で出力
- 見出し、箇条書き、表を適切に使用
- 情報源を明記（URL、出典名）
- 具体的な数値データを含める

## 品質要件
- 最低10個以上の信頼できる情報源を参照
- 2024年の最新情報を重視
- 定量的データに基づく分析
- 実行可能性を考慮した提言

調査完了後、結果全体をコピーして返してください。
"""

            # プロンプト長のチェック
            if len(cursor_prompt) > self.config.max_prompt_length:
                logger.warning(f"プロンプトが長すぎます ({len(cursor_prompt)}文字)。要約版を使用します。")
                cursor_prompt = self._truncate_prompt(cursor_prompt)

            return cursor_prompt
        except Exception as e:
            logger.error(f"プロンプトフォーマット中にエラーが発生: {e}")
            return base_prompt

    def _truncate_prompt(self, prompt: str) -> str:
        """プロンプトを適切な長さに切り詰める"""
        try:
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
        except Exception as e:
            logger.error(f"プロンプト切り詰め中にエラーが発生: {e}")
            return prompt[: self.config.max_prompt_length] + "\n... (プロンプトが長すぎるため省略)"

    def extract_search_queries(self, prompt: str) -> List[str]:
        """プロンプトから検索クエリを抽出"""
        try:
            queries = []

            # 企業名と業界の組み合わせ
            company_pattern = r"企業名[：:]\s*([^\n]+)"
            industry_pattern = r"業界[：:]\s*([^\n]+)"
            market_pattern = r"対象市場[：:]\s*([^\n]+)"

            company_match = re.search(company_pattern, prompt)
            industry_match = re.search(industry_pattern, prompt)
            market_match = re.search(market_pattern, prompt)

            if company_match and industry_match:
                company = company_match.group(1).strip()
                industry = industry_match.group(1).strip()
                queries.append(f"{company} {industry} 市場分析 2024")
                queries.append(f"{company} {industry} 戦略 事例")

            if market_match:
                market = market_match.group(1).strip()
                queries.append(f"{market} トレンド 統計 2024")
                queries.append(f"{market} 市場規模 予測")

            # 競合企業の検索
            competitors_pattern = r"競合企業[：:]\s*([^\n]+)"
            competitors_match = re.search(competitors_pattern, prompt)
            if competitors_match:
                competitors_text = competitors_match.group(1).strip()
                competitors = [c.strip() for c in competitors_text.split(",")]
                for competitor in competitors[:3]:  # 最大3社
                    queries.append(f"{competitor} 戦略 事例")
                    queries.append(f"{competitor} 業績 2024")

            # 重複を除去
            unique_queries = list(set(queries))

            logger.info(f"抽出された検索クエリ: {unique_queries}")
            return unique_queries
        except Exception as e:
            logger.error(f"検索クエリ抽出中にエラーが発生: {e}")
            return []

    def save_cursor_session(self, session_data: Dict[str, Any]) -> Path:
        """Cursorセッションデータの保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_file = self.temp_dir / f"cursor_session_{timestamp}.json"

            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Cursorセッションを保存しました: {session_file}")
            return session_file
        except Exception as e:
            logger.error(f"Cursorセッション保存中にエラーが発生: {e}")
            raise

    def load_cursor_session(self, session_file: Path) -> Dict[str, Any]:
        """Cursorセッションデータの読み込み"""
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            logger.info(f"Cursorセッションを読み込みました: {session_file}")
            return session_data
        except FileNotFoundError as e:
            logger.error(f"Cursorセッションファイルが見つかりません: {session_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"CursorセッションファイルのJSON形式が不正: {e}")
            raise
        except Exception as e:
            logger.error(f"Cursorセッション読み込み中にエラーが発生: {e}")
            raise

    def create_cursor_workspace_config(self, project_name: str) -> Dict[str, Any]:
        """Cursorワークスペース設定の作成"""
        try:
            workspace_config = {
                "project_name": project_name,
                "cursor_settings": {
                    "enable_web_search": self.config.web_search_enabled,
                    "max_prompt_length": self.config.max_prompt_length,
                    "timeout_seconds": self.config.timeout_seconds,
                },
                "research_phases": [
                    "phase_1",
                    "phase_2",
                    "phase_3",
                    "phase_4",
                    "phase_5",
                    "phase_6",
                    "phase_7",
                    "phase_8",
                    "final_phase",
                ],
                "output_directory": str(self.root_dir / "outputs" / project_name),
                "temp_directory": str(self.temp_dir),
            }

            config_file = self.temp_dir / f"cursor_workspace_{project_name}.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(workspace_config, f, ensure_ascii=False, indent=2)

            logger.info(f"Cursorワークスペース設定を作成しました: {config_file}")
            return workspace_config
        except Exception as e:
            logger.error(f"Cursorワークスペース設定作成中にエラーが発生: {e}")
            raise

    def validate_cursor_response(self, response: str) -> Dict[str, Any]:
        """Cursor応答の検証"""
        try:
            validation_result = {
                "valid": True,
                "score": 100,
                "issues": [],
                "warnings": [],
                "recommendations": [],
            }

            # 基本的な検証
            if not response or len(response.strip()) < 100:
                validation_result["valid"] = False
                validation_result["score"] -= 50
                validation_result["issues"].append("応答が短すぎます")

            # マークダウン形式のチェック
            if not re.search(r"^#\s+", response, re.MULTILINE):
                validation_result["score"] -= 10
                validation_result["warnings"].append("見出しが不足しています")

            # 情報源のチェック
            sources = re.findall(r"https?://[^\s\)]+", response)
            if len(sources) < 5:
                validation_result["score"] -= 15
                validation_result["warnings"].append("情報源が不足しています")
            else:
                validation_result["recommendations"].append(
                    f"情報源が十分です ({len(sources)}件)"
                )

            # 数値データのチェック
            numbers = re.findall(r"\d+%|\d+円|\d+万円|\d+億円|\d+社|\d+人", response)
            if len(numbers) < 3:
                validation_result["score"] -= 10
                validation_result["warnings"].append("数値データが不足しています")
            else:
                validation_result["recommendations"].append(
                    f"数値データが十分です ({len(numbers)}件)"
                )

            # スコアの正規化
            validation_result["score"] = max(0, min(100, validation_result["score"]))

            logger.info(f"Cursor応答検証完了: スコア {validation_result['score']}/100")
            return validation_result
        except Exception as e:
            logger.error(f"Cursor応答検証中にエラーが発生: {e}")
            return {
                "valid": False,
                "score": 0,
                "issues": [f"検証エラー: {e}"],
                "warnings": [],
                "recommendations": [],
            }

    def extract_key_insights(self, response: str) -> List[str]:
        """Cursor応答から重要な洞察を抽出"""
        try:
            insights = []

            # 重要なキーワードを含む行を抽出
            important_patterns = [
                r"^.*重要.*$",
                r"^.*結論.*$",
                r"^.*推奨.*$",
                r"^.*発見.*$",
                r"^.*課題.*$",
                r"^.*機会.*$",
                r"^.*戦略.*$",
            ]

            for pattern in important_patterns:
                matches = re.findall(pattern, response, re.MULTILINE)
                insights.extend(matches[:3])  # 各パターンから最大3件

            # 箇条書きから洞察を抽出
            bullet_points = re.findall(r"^\s*[-*+]\s+(.+)$", response, re.MULTILINE)
            for point in bullet_points[:5]:  # 最大5件
                if any(keyword in point for keyword in ["重要", "結論", "推奨", "発見"]):
                    insights.append(point.strip())

            # 重複を除去
            unique_insights = list(set(insights))

            logger.info(f"重要な洞察を {len(unique_insights)} 件抽出しました")
            return unique_insights[:10]  # 最大10件
        except Exception as e:
            logger.error(f"洞察抽出中にエラーが発生: {e}")
            return []

    def create_cursor_summary(self, responses: List[Dict[str, Any]]) -> str:
        """Cursor応答のサマリー作成"""
        try:
            summary = "# Cursor AI 調査サマリー\n\n"

            for i, response_data in enumerate(responses, 1):
                summary += f"## 調査 {i}\n\n"
                summary += f"**テーマ**: {response_data.get('theme_id', 'N/A')}\n"
                summary += f"**ステップ**: {response_data.get('step', 'N/A')}\n"
                summary += (
                    f"**実行時間**: {response_data.get('execution_time', 0):.1f}秒\n\n"
                )

                # 主要な洞察を抽出
                insights = self.extract_key_insights(response_data.get("result", ""))
                if insights:
                    summary += "**主要な洞察**:\n"
                    for insight in insights[:3]:
                        summary += f"- {insight}\n"
                    summary += "\n"

                # 情報源
                sources = response_data.get("sources", [])
                if sources:
                    summary += f"**情報源**: {len(sources)}件\n\n"

                summary += "---\n\n"

            return summary
        except Exception as e:
            logger.error(f"Cursorサマリー作成中にエラーが発生: {e}")
            return f"サマリー作成中にエラーが発生しました: {e}"

    def get_cursor_statistics(self) -> Dict[str, Any]:
        """Cursor統合統計情報の取得"""
        try:
            stats = {
                "config": {
                    "max_prompt_length": self.config.max_prompt_length,
                    "web_search_enabled": self.config.web_search_enabled,
                    "max_retries": self.config.max_retries,
                    "timeout_seconds": self.config.timeout_seconds,
                },
                "directories": {
                    "root_dir": str(self.root_dir),
                    "temp_dir": str(self.temp_dir),
                },
                "temp_files": len(list(self.temp_dir.glob("*.json")))
                if self.temp_dir.exists()
                else 0,
            }

            return stats
        except Exception as e:
            logger.error(f"Cursor統計情報の取得中にエラーが発生: {e}")
            return {"error": str(e)}
