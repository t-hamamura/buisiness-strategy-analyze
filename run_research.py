#!/usr/bin/env python
"""
Business Strategy Research System - 実行スクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import BSRSMain

def main():
    """メインエントリーポイント"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   Business Strategy Research System (BSRS) v1.0.0         ║
║   Powered by Cursor AI                                    ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    app = BSRSMain()
    app.run()

if __name__ == "__main__":
    main() 