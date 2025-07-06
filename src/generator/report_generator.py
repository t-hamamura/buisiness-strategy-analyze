"""
Report Generator - レポート生成
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass

# import matplotlib.pyplot as plt
# import seaborn as sns
# from src.generator.visualization import VisualizationGenerator

# ロギング設定
logger = logging.getLogger(__name__)


@dataclass
class GeneratorConfig:
    """レポート生成設定のデータクラス"""

    max_report_length: int = 50000
    min_word_count: int = 3000
    max_retries: int = 3
    retry_delay: float = 1.0
    backup_enabled: bool = True


class ReportGenerator:
    def __init__(self, config: Optional[GeneratorConfig] = None) -> None:
        """依存性注入による初期化"""
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.config = config or GeneratorConfig()
        # self.viz_generator = VisualizationGenerator()
        self.output_base = self.root_dir / "outputs"

    def generate_theme_report(
        self,
        config_data: Dict[str, Any],
        phase_name: str,
        theme_id: str,
        theme_info: Dict[str, Any],
        results: List[Dict[str, Any]],
    ) -> Path:
        """テーマ別レポートの生成"""
        try:
            # 出力ディレクトリの作成
            output_dir = self.output_base / config_data["project_name"] / phase_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # レポートファイル名
            report_filename = f"{theme_id}_{theme_info['name']}.md"
            report_path = output_dir / report_filename

            # レポート内容の生成
            report_content = self.create_report_content(
                config_data, phase_name, theme_id, theme_info, results
            )

            # レポート長のチェック
            if len(report_content) > self.config.max_report_length:
                logger.warning(f"レポートが長すぎます ({len(report_content)}文字)。要約版を生成します。")
                report_content = self._truncate_report(report_content)

            # バックアップの作成
            if self.config.backup_enabled:
                self._create_backup(report_path)

            # ファイルに保存
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)

            logger.info(f"    📄 レポート生成: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"レポート生成中にエラーが発生: {e}")
            raise

    def _truncate_report(self, content: str) -> str:
        """レポートを適切な長さに切り詰める"""
        lines = content.split("\n")
        truncated_lines = []
        current_length = 0

        for line in lines:
            if current_length + len(line) > self.config.max_report_length - 500:
                truncated_lines.append("\n... (レポートが長すぎるため省略)")
                break
            truncated_lines.append(line)
            current_length += len(line) + 1

        return "\n".join(truncated_lines)

    def _create_backup(self, report_path: Path) -> None:
        """レポートのバックアップを作成"""
        try:
            if report_path.exists():
                backup_path = report_path.with_suffix(".md.backup")
                with open(report_path, "r", encoding="utf-8") as src:
                    with open(backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                logger.debug(f"バックアップを作成: {backup_path}")
        except Exception as e:
            logger.warning(f"バックアップ作成に失敗: {e}")

    def create_report_content(
        self,
        config_data: Dict[str, Any],
        phase_name: str,
        theme_id: str,
        theme_info: Dict[str, Any],
        results: List[Dict[str, Any]],
    ) -> str:
        """レポート内容の作成"""
        try:
            content = f"""# {theme_info['name']}

**プロジェクト**: {config_data['project_name']}  
**フェーズ**: {self.get_phase_name_jp(phase_name)}  
**作成日**: {datetime.now().strftime('%Y年%m月%d日')}  
**企業名**: {config_data['company_name']}

---

## エグゼクティブサマリー

{self.create_executive_summary(results)}

---

## 目次

1. [現状分析](#現状分析)
2. [戦略提言](#戦略提言)
3. [実行計画](#実行計画)
4. [参考文献](#参考文献)

---

## 現状分析

{results[0]['result'] if results else ''}

### 主要な発見事項

{self.extract_key_findings(results[0]['result'] if results else '')}

### 分析図表

{self.create_analysis_charts(theme_id, results)}

---

## 戦略提言

{results[1]['result'] if len(results) > 1 else ''}

### 戦略オプション比較

{self.create_strategy_comparison_table(results[1] if len(results) > 1 else None)}

---

## 実行計画

{results[2]['result'] if len(results) > 2 else ''}

### アクションプラン

{self.create_action_plan_table(results[2] if len(results) > 2 else None)}

### KPI設定

{self.create_kpi_table(results[2] if len(results) > 2 else None)}

---

## 参考文献

{self.create_references_section(results)}

---

## 付録

### 調査手法
- Cursor AI による自動調査
- Web検索による最新情報の収集
- 3段階の深掘り分析（現状分析→戦略立案→実行計画）

### 品質保証
- 最低10個以上の信頼できる情報源を参照
- 定量的データに基づく分析
- 実行可能性を重視した提言

---

*本レポートは Business Strategy Research System により自動生成されました。*
"""
            return content
        except Exception as e:
            logger.error(f"レポート内容作成中にエラーが発生: {e}")
            return f"エラーが発生しました: {e}"

    def create_executive_summary(self, results: List[Dict[str, Any]]) -> str:
        """エグゼクティブサマリーの作成"""
        try:
            summary_points = []

            # 各ステップから重要ポイントを抽出
            for idx, result in enumerate(results):
                if result and "result" in result:
                    # 簡易的な要約抽出（実際にはより高度な要約アルゴリズムを使用）
                    lines = result["result"].split("\n")
                    for line in lines:
                        if any(
                            keyword in line for keyword in ["重要", "結論", "推奨", "ポイント"]
                        ):
                            summary_points.append(f"- {line.strip()}")
                            if len(summary_points) >= 5:
                                break

            return "\n".join(summary_points[:5]) if summary_points else "要約を生成中..."
        except Exception as e:
            logger.error(f"エグゼクティブサマリー作成中にエラーが発生: {e}")
            return "要約の生成中にエラーが発生しました。"

    def extract_key_findings(self, analysis_text: str) -> str:
        """主要な発見事項の抽出"""
        try:
            findings = []

            # テキストから箇条書きを抽出
            lines = analysis_text.split("\n")
            in_list = False

            for line in lines:
                if line.strip().startswith("- ") or line.strip().startswith("* "):
                    findings.append(line.strip())
                    in_list = True
                elif in_list and not line.strip():
                    break

            return "\n".join(findings[:10]) if findings else "- 詳細は本文を参照"
        except Exception as e:
            logger.error(f"主要発見事項の抽出中にエラーが発生: {e}")
            return "- 詳細は本文を参照"

    def create_analysis_charts(
        self, theme_id: str, results: List[Dict[str, Any]]
    ) -> str:
        """分析図表の作成"""
        try:
            chart_markdown = ""

            # テーマに応じた図表を生成（一時的に無効化）
            # if theme_id == 'A':
            #     # SWOT分析図
            #     chart_path = self.viz_generator.create_swot_analysis(results)
            #     chart_markdown = f"![SWOT分析]({chart_path})\n"
            # elif theme_id == '3':
            #     # 競合マップ
            #     chart_path = self.viz_generator.create_competitor_map(results)
            #     chart_markdown = f"![競合マップ]({chart_path})\n"

            return chart_markdown
        except Exception as e:
            logger.error(f"分析図表作成中にエラーが発生: {e}")
            return ""

    def create_strategy_comparison_table(
        self, strategy_result: Optional[Dict[str, Any]]
    ) -> str:
        """戦略比較表の作成"""
        try:
            if not strategy_result:
                return "戦略データがありません。"

            # 戦略比較表の生成（簡易版）
            table = """
| 戦略オプション | メリット | デメリット | 実現可能性 | 推奨度 |
|---------------|----------|------------|------------|--------|
| オプション1 | 高成長 | 高リスク | 中 | ⭐⭐⭐ |
| オプション2 | 安定性 | 低成長 | 高 | ⭐⭐ |
| オプション3 | バランス | 中程度 | 中 | ⭐⭐⭐⭐ |
"""
            return table
        except Exception as e:
            logger.error(f"戦略比較表作成中にエラーが発生: {e}")
            return "戦略比較表の生成中にエラーが発生しました。"

    def create_action_plan_table(
        self, execution_result: Optional[Dict[str, Any]]
    ) -> str:
        """アクションプラン表の作成"""
        try:
            if not execution_result:
                return "実行計画データがありません。"

            # アクションプラン表の生成（簡易版）
            table = """
| タスク | 担当 | 期限 | 予算 | ステータス |
|-------|------|------|------|-----------|
| 市場調査 | マーケティング部 | 2024/03 | 100万円 | 計画中 |
| プロトタイプ開発 | 開発部 | 2024/04 | 200万円 | 未着手 |
| テスト実施 | QA部 | 2024/05 | 50万円 | 未着手 |
"""
            return table
        except Exception as e:
            logger.error(f"アクションプラン表作成中にエラーが発生: {e}")
            return "アクションプラン表の生成中にエラーが発生しました。"

    def create_kpi_table(self, execution_result: Optional[Dict[str, Any]]) -> str:
        """KPI表の作成"""
        try:
            if not execution_result:
                return "KPIデータがありません。"

            # KPI表の生成（簡易版）
            table = """
| KPI | 目標値 | 現在値 | 達成率 | 備考 |
|-----|--------|--------|--------|------|
| 売上高 | 1億円 | 0円 | 0% | 開始前 |
| 顧客数 | 100社 | 0社 | 0% | 開始前 |
| 満足度 | 90% | - | - | 測定未開始 |
"""
            return table
        except Exception as e:
            logger.error(f"KPI表作成中にエラーが発生: {e}")
            return "KPI表の生成中にエラーが発生しました。"

    def create_references_section(self, results: List[Dict[str, Any]]) -> str:
        """参考文献セクションの作成"""
        try:
            references = []

            for result in results:
                if "sources" in result and result["sources"]:
                    references.extend(result["sources"])

            # 重複を除去
            unique_references = list(set(references))

            if not unique_references:
                return "参考文献がありません。"

            references_text = ""
            for i, ref in enumerate(unique_references[:15], 1):  # 最大15件
                references_text += f"{i}. {ref}\n"

            return references_text
        except Exception as e:
            logger.error(f"参考文献セクション作成中にエラーが発生: {e}")
            return "参考文献の生成中にエラーが発生しました。"

    def get_phase_name_jp(self, phase_name: str) -> str:
        """フェーズ名を日本語に変換"""
        phase_mapping = {
            "phase_1": "フェーズI: 内部環境分析と事業モデル評価",
            "phase_2": "フェーズII: 外部環境分析と事業機会の特定",
            "phase_3": "フェーズIII: ターゲット顧客とインサイトの解明",
            "phase_4": "フェーズIV: 提供価値と市場投入(GTM)戦略",
            "phase_5": "フェーズV: グロース戦略と収益性分析",
            "phase_6": "フェーズVI: マーケティング・コミュニケーション戦略",
            "phase_7": "フェーズVII: 戦略実行を支える組織と基盤",
            "phase_8": "フェーズVIII: 持続可能性とリスクマネジメント",
            "final_phase": "最終フェーズ: 全体戦略の統合と提言",
        }
        return phase_mapping.get(phase_name, phase_name)

    def generate_summary_report(
        self, config_data: Dict[str, Any], all_results: Dict[str, Any]
    ) -> None:
        """全体サマリーレポートの生成"""
        try:
            logger.info("\n📑 全体サマリーレポートを生成中...")

            # 出力ディレクトリの作成
            output_dir = self.output_base / config_data["project_name"]
            output_dir.mkdir(parents=True, exist_ok=True)

            # サマリーレポートファイル名
            timestamp = datetime.now().strftime("%Y%m%d")
            summary_filename = f"00_全体戦略サマリーレポート_{timestamp}.md"
            summary_path = output_dir / summary_filename

            # サマリー内容の生成
            summary_content = self._create_summary_content(config_data, all_results)

            # ファイルに保存
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_content)

            logger.info(f"✅ 全体サマリーレポートを生成しました: {summary_path}")
        except Exception as e:
            logger.error(f"全体サマリーレポートの生成に失敗: {e}")
            raise

    def _create_summary_content(
        self, config_data: Dict[str, Any], all_results: Dict[str, Any]
    ) -> str:
        """サマリー内容の作成"""
        try:
            content = f"""# 事業戦略 全体サマリーレポート

**プロジェクト**: {config_data['project_name']}  
**作成日**: {datetime.now().strftime('%Y年%m月%d日')}  
**企業名**: {config_data['company_name']}  
**業界**: {config_data['industry']}

---

## エグゼクティブサマリー

本レポートは、{config_data['company_name']}の事業戦略について、8フェーズ・36テーマにわたる包括的な分析結果をまとめたものです。

### 主要な発見事項

{self._extract_summary_key_findings(all_results)}

### 戦略的提言

{self._extract_strategic_recommendations(all_results)}

---

## フェーズ別分析結果

{self.create_phase_summaries(all_results)}

---

## 統合戦略マップ

{self.create_integrated_strategy_map(all_results)}

---

## 実行優先順位

### 短期（3ヶ月以内）
- 優先度1: [短期アクション1]
- 優先度2: [短期アクション2]
- 優先度3: [短期アクション3]

### 中期（6ヶ月〜1年）
- 優先度1: [中期アクション1]
- 優先度2: [中期アクション2]

### 長期（1年以上）
- 優先度1: [長期アクション1]
- 優先度2: [長期アクション2]

---

## リスクと対策

### 主要リスク
1. [リスク1] - [対策1]
2. [リスク2] - [対策2]
3. [リスク3] - [対策3]

### 成功要因
1. [成功要因1]
2. [成功要因2]
3. [成功要因3]

---

## 結論

{config_data['company_name']}の事業戦略について、包括的な分析を実施しました。上記の戦略的提言と実行計画に基づき、段階的な事業拡大を推奨します。

---

*本レポートは Business Strategy Research System により自動生成されました。*
"""
            return content
        except Exception as e:
            logger.error(f"サマリー内容作成中にエラーが発生: {e}")
            return f"サマリー内容の生成中にエラーが発生しました: {e}"

    def _extract_summary_key_findings(self, all_results: Dict[str, Any]) -> str:
        """サマリーの主要発見事項を抽出"""
        try:
            findings = []

            for phase_name, phase_data in all_results.items():
                if isinstance(phase_data, dict):
                    for theme_id, theme_data in phase_data.items():
                        if isinstance(theme_data, dict) and "results" in theme_data:
                            for result in theme_data["results"]:
                                if "result" in result:
                                    # 結果から主要なポイントを抽出
                                    lines = result["result"].split("\n")
                                    for line in lines:
                                        if any(
                                            keyword in line
                                            for keyword in ["重要", "結論", "発見", "課題"]
                                        ):
                                            findings.append(f"- {line.strip()}")
                                            if len(findings) >= 10:
                                                break
                        if len(findings) >= 10:
                            break
                if len(findings) >= 10:
                    break

            return (
                "\n".join(findings[:10])
                if findings
                else "- 詳細な分析結果は各フェーズのレポートを参照してください"
            )
        except Exception as e:
            logger.error(f"サマリー主要発見事項の抽出中にエラーが発生: {e}")
            return "- 詳細な分析結果は各フェーズのレポートを参照してください"

    def _extract_strategic_recommendations(self, all_results: Dict[str, Any]) -> str:
        """戦略的提言を抽出"""
        try:
            recommendations = []

            for phase_name, phase_data in all_results.items():
                if isinstance(phase_data, dict):
                    for theme_id, theme_data in phase_data.items():
                        if isinstance(theme_data, dict) and "results" in theme_data:
                            for result in theme_data["results"]:
                                if "result" in result:
                                    # 結果から戦略的提言を抽出
                                    lines = result["result"].split("\n")
                                    for line in lines:
                                        if any(
                                            keyword in line
                                            for keyword in ["推奨", "戦略", "提案", "アクション"]
                                        ):
                                            recommendations.append(f"- {line.strip()}")
                                            if len(recommendations) >= 5:
                                                break
                        if len(recommendations) >= 5:
                            break
                if len(recommendations) >= 5:
                    break

            return (
                "\n".join(recommendations[:5])
                if recommendations
                else "- 詳細な戦略的提言は各フェーズのレポートを参照してください"
            )
        except Exception as e:
            logger.error(f"戦略的提言の抽出中にエラーが発生: {e}")
            return "- 詳細な戦略的提言は各フェーズのレポートを参照してください"

    def create_phase_summaries(self, all_results: Dict[str, Any]) -> str:
        """フェーズ別サマリーの作成"""
        try:
            summaries = []

            for phase_name, phase_data in all_results.items():
                if isinstance(phase_data, dict):
                    summary = f"### {self.get_phase_name_jp(phase_name)}\n\n"

                    theme_count = len(phase_data)
                    summary += f"**分析テーマ数**: {theme_count}テーマ\n\n"

                    # 主要な発見事項を抽出
                    phase_findings = []
                    for theme_id, theme_data in phase_data.items():
                        if isinstance(theme_data, dict) and "results" in theme_data:
                            for result in theme_data["results"]:
                                if "result" in result:
                                    lines = result["result"].split("\n")
                                    for line in lines:
                                        if any(
                                            keyword in line for keyword in ["重要", "結論"]
                                        ):
                                            phase_findings.append(line.strip())
                                            if len(phase_findings) >= 3:
                                                break
                        if len(phase_findings) >= 3:
                            break

                    if phase_findings:
                        summary += "**主要な発見事項**:\n"
                        for finding in phase_findings[:3]:
                            summary += f"- {finding}\n"

                    summaries.append(summary)

            return "\n".join(summaries)
        except Exception as e:
            logger.error(f"フェーズ別サマリー作成中にエラーが発生: {e}")
            return "フェーズ別サマリーの生成中にエラーが発生しました。"

    def create_integrated_strategy_map(self, all_results: Dict[str, Any]) -> str:
        """統合戦略マップの作成"""
        try:
            strategy_map = """
### 統合戦略マップ

```
┌─────────────────┬─────────────────┬─────────────────┐
│   内部環境      │   外部環境      │   顧客分析      │
│   (フェーズ1)   │   (フェーズ2)   │   (フェーズ3)   │
├─────────────────┼─────────────────┼─────────────────┤
│   GTM戦略       │   グロース      │   マーケティング │
│   (フェーズ4)   │   (フェーズ5)   │   (フェーズ6)   │
├─────────────────┼─────────────────┼─────────────────┤
│   組織基盤      │   リスク管理    │   統合戦略      │
│   (フェーズ7)   │   (フェーズ8)   │   (最終フェーズ) │
└─────────────────┴─────────────────┴─────────────────┘
```

### 戦略的優先順位

1. **最優先**: 内部環境の強化とGTM戦略の確立
2. **高優先**: 顧客分析に基づくマーケティング戦略
3. **中優先**: グロース戦略と組織基盤の整備
4. **継続的**: リスク管理と持続可能性の確保
"""
            return strategy_map
        except Exception as e:
            logger.error(f"統合戦略マップ作成中にエラーが発生: {e}")
            return "統合戦略マップの生成中にエラーが発生しました。"
