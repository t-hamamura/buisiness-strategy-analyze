"""
Research Controller - 調査実行の制御
"""
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from src.engine.research_engine import ResearchEngine
from src.generator.report_generator import ReportGenerator
from src.utils.validators import QualityChecker

# ロギング設定
logger = logging.getLogger(__name__)


class ResearchEngineProtocol(Protocol):
    """Research Engine のプロトコル定義"""

    def execute_research(
        self,
        config_data: Dict[str, Any],
        phase_name: str,
        theme_id: str,
        step: int,
        previous_results: Optional[Dict[str, Any]] = None,
        theme_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        ...


class ReportGeneratorProtocol(Protocol):
    """Report Generator のプロトコル定義"""

    def generate_theme_report(
        self,
        config_data: Dict[str, Any],
        phase_name: str,
        theme_id: str,
        theme_info: Dict[str, Any],
        results: List[Dict[str, Any]],
    ) -> Path:
        ...

    def generate_summary_report(
        self, config_data: Dict[str, Any], all_results: Dict[str, Any]
    ) -> None:
        ...


class QualityCheckerProtocol(Protocol):
    """Quality Checker のプロトコル定義"""

    def check_report(self, report_path: Path) -> Dict[str, Any]:
        ...


@dataclass
class ResearchConfig:
    """調査設定のデータクラス"""

    max_retries: int = 3
    retry_delay: float = 2.0
    timeout_seconds: int = 300
    api_rate_limit_delay: float = 1.0
    phase_delay: float = 2.0


class ResearchController:
    def __init__(
        self,
        research_engine: Optional[ResearchEngineProtocol] = None,
        report_generator: Optional[ReportGeneratorProtocol] = None,
        quality_checker: Optional[QualityCheckerProtocol] = None,
        config: Optional[ResearchConfig] = None,
    ) -> None:
        """依存性注入による初期化"""
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.research_engine = research_engine or ResearchEngine()
        self.report_generator = report_generator or ReportGenerator()
        self.quality_checker = quality_checker or QualityChecker()
        self.config = config or ResearchConfig()
        self.phase_results: Dict[str, Any] = {}

    def run_full_research(self, config_data: Dict[str, Any]) -> None:
        """全体調査の実行"""
        logger.info(f"\n🚀 {config_data['project_name']} の全体調査を開始します...")
        start_time = time.time()

        # 全フェーズを順次実行
        phases = [
            "phase_1",
            "phase_2",
            "phase_3",
            "phase_4",
            "phase_5",
            "phase_6",
            "phase_7",
            "phase_8",
            "final_phase",
        ]

        for phase in phases:
            logger.info(f"\n📊 {phase} を実行中...")
            try:
                self.run_phase_research(config_data, phase)
                # フェーズ間で少し待機（API制限対策）
                time.sleep(self.config.phase_delay)
            except Exception as e:
                logger.error(f"フェーズ {phase} の実行中にエラーが発生: {e}")
                continue

        elapsed_time = time.time() - start_time
        logger.info(f"\n✅ 全体調査が完了しました！ (所要時間: {elapsed_time/60:.1f}分)")
        self.generate_summary_report(config_data)

    def run_phase_research(self, config_data: Dict[str, Any], phase_name: str) -> None:
        """フェーズ単位での調査実行"""
        # フェーズ設定の読み込み
        try:
            phase_config = self.load_phase_config(phase_name)
        except Exception as e:
            logger.error(f"フェーズ設定の読み込みに失敗: {e}")
            return

        phase_results = {}

        for theme_id, theme_info in phase_config["themes"].items():
            logger.info(f"\n  📝 {theme_id}: {theme_info['name']} を調査中...")

            # 3段階の深掘り調査
            theme_results = []
            for step in range(1, 4):
                try:
                    # 前のフェーズの結果を参照
                    previous_results = self.get_previous_results(phase_name, theme_id)

                    # 調査実行（リトライ機能付き）
                    result = self._execute_research_with_retry(
                        config_data=config_data,
                        phase_name=phase_name,
                        theme_id=theme_id,
                        step=step,
                        previous_results=previous_results,
                        theme_results=theme_results,
                    )

                    theme_results.append(result)
                    logger.info(f"    ✓ ステップ {step}/3 完了")
                    time.sleep(self.config.api_rate_limit_delay)  # API制限対策
                except Exception as e:
                    logger.error(f"ステップ {step} の実行中にエラーが発生: {e}")
                    continue

            # レポート生成
            try:
                report_path = self.report_generator.generate_theme_report(
                    config_data=config_data,
                    phase_name=phase_name,
                    theme_id=theme_id,
                    theme_info=theme_info,
                    results=theme_results,
                )

                # 品質チェック
                quality_result = self.quality_checker.check_report(report_path)
                if quality_result["passed"]:
                    logger.info(f"    ✅ 品質チェック合格")
                else:
                    logger.warning(f"    ⚠️  品質チェック要改善: {quality_result['issues']}")

                phase_results[theme_id] = {
                    "results": theme_results,
                    "report_path": report_path,
                    "quality": quality_result,
                }
            except Exception as e:
                logger.error(f"レポート生成中にエラーが発生: {e}")

        # フェーズ結果を保存
        self.phase_results[phase_name] = phase_results
        self.save_phase_results(config_data, phase_name, phase_results)

    def _execute_research_with_retry(
        self,
        config_data: Dict[str, Any],
        phase_name: str,
        theme_id: str,
        step: int,
        previous_results: Optional[Dict[str, Any]] = None,
        theme_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """リトライ機能付きの調査実行"""
        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                return self.research_engine.execute_research(
                    config_data=config_data,
                    phase_name=phase_name,
                    theme_id=theme_id,
                    step=step,
                    previous_results=previous_results,
                    theme_results=theme_results,
                )
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"調査実行試行 {attempt + 1}/{self.config.max_retries} が失敗: {e}"
                )

                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)

        # すべてのリトライが失敗
        logger.error(f"調査実行が {self.config.max_retries} 回試行後も失敗: {last_exception}")
        raise last_exception

    def get_previous_results(
        self, current_phase: str, theme_id: str
    ) -> Optional[Dict[str, Any]]:
        """前フェーズの結果を取得"""
        # フェーズ番号を取得
        if current_phase == "final_phase":
            # 最終フェーズは全フェーズの結果を参照
            return self.phase_results

        try:
            phase_num = int(current_phase.split("_")[1])
            if phase_num == 1:
                return None

            # 前フェーズの結果を返す
            previous_phase = f"phase_{phase_num - 1}"
            return self.phase_results.get(previous_phase, None)
        except (ValueError, IndexError):
            logger.warning(f"フェーズ番号の解析に失敗: {current_phase}")
            return None

    def load_phase_config(self, phase_name: str) -> Dict[str, Any]:
        """フェーズ設定の読み込み"""
        config_path = self.root_dir / "config" / "phase_config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                all_phases = json.load(f)
            return all_phases.get(phase_name, {})
        except FileNotFoundError as e:
            logger.error(f"フェーズ設定ファイルが見つかりません: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"フェーズ設定ファイルのJSON形式が不正: {e}")
            raise
        except Exception as e:
            logger.error(f"フェーズ設定ファイルの読み込みに失敗: {e}")
            raise

    def save_phase_results(
        self, config_data: Dict[str, Any], phase_name: str, results: Dict[str, Any]
    ) -> None:
        """フェーズ結果の保存"""
        try:
            output_dir = (
                self.root_dir / "outputs" / config_data["project_name"] / phase_name
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            results_file = output_dir / "phase_results.json"
            # 保存用にシリアライズ可能な形式に変換
            serializable_results = {
                theme_id: {
                    "report_path": str(data["report_path"]),
                    "quality": data["quality"],
                }
                for theme_id, data in results.items()
            }

            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"フェーズ結果の保存に失敗: {e}")
            raise

    def generate_summary_report(self, config_data: Dict[str, Any]) -> None:
        """全体サマリーレポートの生成"""
        logger.info("\n📑 全体サマリーレポートを生成中...")
        try:
            self.report_generator.generate_summary_report(
                config_data=config_data, all_results=self.phase_results
            )
        except Exception as e:
            logger.error(f"サマリーレポートの生成に失敗: {e}")
            raise

    def run_single_theme(
        self, config_data: Dict[str, Any], phase_name: str, theme_id: str
    ) -> None:
        """単一テーマの実行"""
        try:
            phase_config = self.load_phase_config(phase_name)
            theme_info = phase_config["themes"].get(theme_id)

            if not theme_info:
                logger.error(f"❌ テーマ {theme_id} が見つかりません。")
                return

            logger.info(f"\n📝 {theme_id}: {theme_info['name']} を調査中...")

            # 3段階の深掘り調査
            theme_results = []
            for step in range(1, 4):
                try:
                    previous_results = self.get_previous_results(phase_name, theme_id)

                    result = self._execute_research_with_retry(
                        config_data=config_data,
                        phase_name=phase_name,
                        theme_id=theme_id,
                        step=step,
                        previous_results=previous_results,
                        theme_results=theme_results,
                    )

                    theme_results.append(result)
                    logger.info(f"    ✓ ステップ {step}/3 完了")
                    time.sleep(self.config.api_rate_limit_delay)
                except Exception as e:
                    logger.error(f"ステップ {step} の実行中にエラーが発生: {e}")
                    continue

            # レポート生成
            try:
                report_path = self.report_generator.generate_theme_report(
                    config_data=config_data,
                    phase_name=phase_name,
                    theme_id=theme_id,
                    theme_info=theme_info,
                    results=theme_results,
                )

                # 品質チェック
                quality_result = self.quality_checker.check_report(report_path)
                if quality_result["passed"]:
                    logger.info(f"    ✅ 品質チェック合格")
                else:
                    logger.warning(f"    ⚠️  品質チェック要改善: {quality_result['issues']}")

                logger.info(f"✅ テーマ {theme_id} の調査が完了しました")
                logger.info(f"📄 レポート: {report_path}")

            except Exception as e:
                logger.error(f"レポート生成中にエラーが発生: {e}")

        except Exception as e:
            logger.error(f"単一テーマ実行中にエラーが発生: {e}")
            raise
