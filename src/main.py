"""
Business Strategy Research System - Main Entry Point
"""
import sys
import argparse
from pathlib import Path
from src.controller.research_controller import ResearchController
from src.utils.config_reader import ConfigReader

class BSRSMain:
    def __init__(self):
        self.config_reader = ConfigReader()
        self.controller = ResearchController()
    
    def interactive_mode(self):
        """対話モードでの実行"""
        print("🎯 Business Strategy Research System へようこそ！")
        print("-" * 50)
        
        # 設定ファイルの確認
        config_file = self.config_reader.find_config_file()
        if not config_file:
            print("❌ 事前調査ファイルが見つかりません。")
            print("💡 templates/research_config_template.md をコピーして")
            print("   必要事項を記入し、project_config.md として保存してください。")
            return
        
        print(f"✅ 設定ファイルを読み込みました: {config_file}")
        config_data = self.config_reader.load_config(config_file)
        
        # 実行モードの選択
        print("\n実行モードを選択してください:")
        print("1. 全体調査を実行")
        print("2. フェーズを選択して実行")
        print("3. テーマを選択して実行")
        print("4. 品質チェックと再実行")
        
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
            print("❌ 無効な選択です。")
    
    def select_phase_mode(self, config_data):
        """フェーズ選択モード"""
        print("\n実行するフェーズを選択してください:")
        phases = [
            "1. フェーズI: 内部環境分析と事業モデル評価",
            "2. フェーズII: 外部環境分析と事業機会の特定",
            "3. フェーズIII: ターゲット顧客とインサイトの解明",
            "4. フェーズIV: 提供価値と市場投入(GTM)戦略",
            "5. フェーズV: グロース戦略と収益性分析",
            "6. フェーズVI: マーケティング・コミュニケーション戦略",
            "7. フェーズVII: 戦略実行を支える組織と基盤",
            "8. フェーズVIII: 持続可能性とリスクマネジメント",
            "9. 最終フェーズ: 全体戦略の統合と提言"
        ]
        for phase in phases:
            print(phase)
        
        choice = input("\n選択 (1-9): ")
        phase_map = {str(i): f"phase_{i}" for i in range(1, 9)}
        phase_map["9"] = "final_phase"
        
        if choice in phase_map:
            self.controller.run_phase_research(config_data, phase_map[choice])
        else:
            print("❌ 無効な選択です。")
    
    def run(self):
        """メイン実行"""
        self.interactive_mode()

if __name__ == "__main__":
    app = BSRSMain()
    app.run() 