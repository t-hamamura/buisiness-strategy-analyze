"""
Business Strategy Research System - Main Entry Point
"""
import sys
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from src.controller.research_controller import ResearchController
from src.utils.config_reader import ConfigReader

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class BSRSMain:
    def __init__(self) -> None:
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.config_reader = ConfigReader()
        self.controller = ResearchController()

    def interactive_mode(self) -> None:
        """対話モードの実行"""
        logger.info("\n--- Business Strategy Research System ---\n")

        # 設定ファイルの確認
        config_file = self.config_reader.find_config_file()
        if not config_file:
            logger.error("❌ 設定ファイルが見つかりません。")
            logger.info("\n【初回セットアップ手順】")
            logger.info("1. project_config.md.example をコピー")
            logger.info("2. project_config.md として保存")
            logger.info("3. 必要事項を記入")
            logger.info("4. 再度このスクリプトを実行")
            return

        logger.info(f"✅ 設定ファイルを読み込みました: {config_file}")
        try:
            config_data = self.config_reader.load_config(config_file)
        except Exception as e:
            logger.error(f"❌ 設定ファイルの読み込みに失敗しました: {e}")
            return

        # 設定内容の確認
        logger.info("\n【調査対象の確認】")
        logger.info(f"企業名: {config_data.get('company_name', '未設定')}")
        logger.info(f"業界: {config_data.get('industry', '未設定')}")
        logger.info(f"製品/サービス: {config_data.get('product_service', '未設定')}")

        confirm = input("\nこの内容で調査を開始しますか？ (y/n): ")
        if confirm.lower() != "y":
            logger.info("設定ファイルを修正してから再実行してください。")
            return

        # 実行モードの選択
        logger.info("\n実行モードを選択してください:")
        logger.info("1. 全体調査を実行")
        logger.info("2. フェーズを選択して実行")
        logger.info("3. テーマを選択して実行")
        logger.info("4. 品質チェックと再実行")

        choice = input("\n選択 (1-4): ")

        if choice == "1":
            self.controller.run_full_research(config_data)
        elif choice == "2":
            self.select_phase_mode(config_data)
        elif choice == "3":
            self.select_theme_mode(config_data)
        elif choice == "4":
            self.quality_check_mode(config_data)
        else:
            logger.error("❌ 無効な選択です。")

    def select_phase_mode(self, config_data: Dict[str, Any]) -> None:
        """フェーズ選択モード"""
        logger.info("\n実行するフェーズを選択してください:")
        phases = [
            "1. フェーズI: 内部環境分析と事業モデル評価",
            "2. フェーズII: 外部環境分析と事業機会の特定",
            "3. フェーズIII: ターゲット顧客とインサイトの解明",
            "4. フェーズIV: 提供価値と市場投入(GTM)戦略",
            "5. フェーズV: グロース戦略と収益性分析",
            "6. フェーズVI: マーケティング・コミュニケーション戦略",
            "7. フェーズVII: 戦略実行を支える組織と基盤",
            "8. フェーズVIII: 持続可能性とリスクマネジメント",
            "9. 最終フェーズ: 全体戦略の統合と提言",
        ]
        for phase in phases:
            logger.info(phase)

        choice = input("\n選択 (1-9): ")
        phase_map = {str(i): f"phase_{i}" for i in range(1, 9)}
        phase_map["9"] = "final_phase"

        if choice in phase_map:
            self.controller.run_phase_research(config_data, phase_map[choice])
        else:
            logger.error("❌ 無効な選択です。")

    def select_theme_mode(self, config_data: Dict[str, Any]) -> None:
        """全36テーマから選択可能にする"""
        logger.info("\n実行するテーマを選択してください:")

        # テーマをグループ化して表示
        theme_groups = [
            ("内部環境分析", ["A", "B"]),
            ("外部環境分析", ["1", "2", "3", "4"]),
            ("顧客分析", ["5", "6", "7"]),
            ("GTM戦略", ["8", "9", "10", "11", "12"]),
            ("グロース戦略", ["13", "14", "15"]),
            (
                "マーケティング戦略",
                ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"],
            ),
            ("組織基盤", ["27", "28", "29", "30", "31", "32"]),
            ("リスク管理", ["33", "34", "35"]),
            ("統合戦略", ["Z"]),
        ]

        all_themes: List[Tuple[str, Dict[str, Any]]] = []
        for group_name, theme_ids in theme_groups:
            logger.info(f"\n【{group_name}】")
            for theme_id in theme_ids:
                theme_info = self.get_theme_info(theme_id)
                if theme_info:
                    idx = len(all_themes) + 1
                    all_themes.append((theme_id, theme_info))
                    logger.info(f"{idx:2d}. [{theme_id:>3}] {theme_info['name']}")
                else:
                    logger.info(f"    [{theme_id:>3}] (データ未定義)")

        if not all_themes:
            logger.error("\n❌ 利用可能なテーマがありません")
            return

        choice = input(f"\n選択 (1-{len(all_themes)}): ")

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(all_themes):
                theme_id, theme_info = all_themes[idx]
                phase_name = self.get_phase_for_theme(theme_id)
                self.controller.run_single_theme(config_data, phase_name, theme_id)
            else:
                logger.error("❌ 無効な選択です。")
        except ValueError:
            logger.error("❌ 数字を入力してください。")

    def get_theme_info(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """テーマIDからテーマ情報を取得"""
        try:
            prompts_data_path = self.root_dir / "prompts_data.json"
            with open(prompts_data_path, "r", encoding="utf-8") as f:
                prompts_data = json.load(f)

            # 全フェーズから該当テーマを検索
            for phase_name, phase_data in prompts_data.items():
                if theme_id in phase_data:
                    return phase_data[theme_id]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            logger.debug(f"テーマ情報の取得に失敗: {e}")

        return None

    def get_phase_for_theme(self, theme_id: str) -> str:
        """テーマIDからフェーズ名を取得"""
        phase_mapping = {
            "A": "phase_1",
            "B": "phase_1",
            "1": "phase_2",
            "2": "phase_2",
            "3": "phase_2",
            "4": "phase_2",
            "5": "phase_3",
            "6": "phase_3",
            "7": "phase_3",
            "8": "phase_4",
            "9": "phase_4",
            "10": "phase_4",
            "11": "phase_4",
            "12": "phase_4",
            "13": "phase_5",
            "14": "phase_5",
            "15": "phase_5",
            "16": "phase_6",
            "17": "phase_6",
            "18": "phase_6",
            "19": "phase_6",
            "20": "phase_6",
            "21": "phase_6",
            "22": "phase_6",
            "23": "phase_6",
            "24": "phase_6",
            "25": "phase_6",
            "26": "phase_6",
            "27": "phase_7",
            "28": "phase_7",
            "29": "phase_7",
            "30": "phase_7",
            "31": "phase_7",
            "32": "phase_7",
            "33": "phase_8",
            "34": "phase_8",
            "35": "phase_8",
            "Z": "final_phase",
        }
        return phase_mapping.get(theme_id, "phase_1")

    def quality_check_mode(self, config_data: Dict[str, Any]) -> None:
        """品質チェックモード"""
        logger.info("\n品質チェックを実行します...")

        from src.utils.validators import QualityChecker

        quality_checker = QualityChecker()
        output_dir = self.root_dir / "outputs" / config_data["project_name"]

        if not output_dir.exists():
            logger.error("❌ まだレポートが生成されていません。")
            return

        # すべてのレポートをチェック
        all_reports = list(output_dir.rglob("*.md"))
        issues_found = False

        for report_path in all_reports:
            if "00_全体戦略サマリー" not in str(report_path):
                try:
                    result = quality_checker.check_report(report_path)
                    if not result["passed"]:
                        issues_found = True
                        logger.warning(f"\n⚠️  {report_path.name}")
                        for issue in result["issues"]:
                            logger.warning(f"   - {issue}")
                except Exception as e:
                    logger.error(f"レポートチェック中にエラーが発生: {e}")

        if not issues_found:
            logger.info("\n✅ すべてのレポートが品質基準を満たしています。")
        else:
            logger.warning("\n品質改善が必要なレポートがあります。")
            retry = input("再実行しますか？ (y/n): ")
            if retry.lower() == "y":
                # TODO: 品質基準を満たさないレポートのみ再実行
                logger.info("再実行機能は開発中です。")

    def run(self) -> None:
        """メイン実行"""
        self.interactive_mode()


if __name__ == "__main__":
    app = BSRSMain()
    app.run()
