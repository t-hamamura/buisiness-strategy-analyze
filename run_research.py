#!/usr/bin/env python
"""
Business Strategy Research System - 実行スクリプト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """メインエントリーポイント"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   Business Strategy Research System (BSRS) v1.0.0         ║
║   Powered by Cursor AI                                    ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 初回セットアップチェック
    if not Path('config/system_config.json').exists():
        print("🔧 初回セットアップを実行します...")
        os.system('python setup.py')
        print()
    
    # プロンプトファイルの生成チェック
    if not Path('prompts/phase_1/A_step1.md').exists():
        print("📝 プロンプトファイルを生成します...")
        os.system('python create_prompts.py')
        print()
    
    from src.main import BSRSMain
    app = BSRSMain()
    app.run()

if __name__ == "__main__":
    main() 