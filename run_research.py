#!/usr/bin/env python
"""
Business Strategy Research System - 実行スクリプト
"""
import sys
import subprocess
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))


def main() -> None:
    """メインエントリーポイント"""
    logger.info(
        """
╔═══════════════════════════════════════════════════════════╗
║   Business Strategy Research System (BSRS) v1.0.0         ║
║   Powered by Cursor AI                                    ║
╚═══════════════════════════════════════════════════════════╝
    """
    )

    # 初回セットアップチェック
    system_config_path = project_root / "config" / "system_config.json"
    if not system_config_path.exists():
        logger.info("🔧 初回セットアップを実行します...")
        try:
            subprocess.run([sys.executable, "setup.py"], check=True, cwd=project_root)
            logger.info("✅ セットアップが完了しました")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ セットアップに失敗しました: {e}")
            sys.exit(1)
        logger.info("")

    # プロンプトファイルの生成チェック
    prompt_file_path = project_root / "prompts" / "phase_1" / "A_step1.md"
    if not prompt_file_path.exists():
        logger.info("📝 プロンプトファイルを生成します...")
        try:
            subprocess.run(
                [sys.executable, "create_prompts.py"], check=True, cwd=project_root
            )
            logger.info("✅ プロンプトファイルの生成が完了しました")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ プロンプトファイルの生成に失敗しました: {e}")
            sys.exit(1)
        logger.info("")

    from src.main import BSRSMain

    app = BSRSMain()
    app.run()


if __name__ == "__main__":
    main()
