"""
Business Strategy Research System - Main Entry Point
"""
import sys
import argparse
from pathlib import Path
from src.controller.research_controller import ResearchController
from src.utils.config_reader import ConfigReader
import json

class BSRSMain:
    def __init__(self):
        self.config_reader = ConfigReader()
        self.controller = ResearchController()
    
    def interactive_mode(self):
        """対話モードの実行（エラーハンドリング・テンプレート自動コピー付き）"""
        import shutil
        from pathlib import Path
        print("\n--- 対話モード開始 ---\n")
        try:
            # テンプレート自動コピー
            template_dir = Path('templates')
            prompts_dir = Path('prompts')
            if template_dir.exists():
                for item in template_dir.glob('**/*'):
                    rel_path = item.relative_to(template_dir)
                    dest = prompts_dir / rel_path
                    if item.is_file() and not dest.exists():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(item, dest)
                        print(f"テンプレート {rel_path} を prompts/ にコピーしました")
            
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
                
        except Exception as e:
            print(f"[エラー] 対話モードで問題が発生しました: {e}")
            import traceback
            traceback.print_exc()
        print("\n--- 対話モード終了 ---\n")
    
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
    
    def select_theme_mode(self, config_data):
        """全36テーマから選択可能にする"""
        print("\n実行するテーマを選択してください:")
        
        # テーマをグループ化して表示
        theme_groups = [
            ("内部環境分析", ["A", "B"]),
            ("外部環境分析", ["1", "2", "3", "4"]),
            ("顧客分析", ["5", "6", "7"]),
            ("GTM戦略", ["8", "9", "10", "11", "12"]),
            ("グロース戦略", ["13", "14", "15"]),
            ("マーケティング戦略", ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"]),
            ("組織基盤", ["27", "28", "29", "30", "31", "32"]),
            ("リスク管理", ["33", "34", "35"]),
            ("統合戦略", ["Z"])
        ]
        
        all_themes = []
        for group_name, theme_ids in theme_groups:
            print(f"\n【{group_name}】")
            for theme_id in theme_ids:
                theme_info = self.get_theme_info(theme_id)
                if theme_info:
                    idx = len(all_themes) + 1
                    all_themes.append((theme_id, theme_info))
                    print(f"{idx:2d}. [{theme_id:>3}] {theme_info['name']}")
                else:
                    print(f"    [{theme_id:>3}] (データ未定義)")
        
        if not all_themes:
            print("\n❌ 利用可能なテーマがありません")
            return
        
        choice = input(f"\n選択 (1-{len(all_themes)}): ")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(all_themes):
                theme_id, theme_info = all_themes[idx]
                phase_name = self.get_phase_for_theme(theme_id)
                self.controller.run_single_theme(config_data, phase_name, theme_id)
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def get_theme_info(self, theme_id):
        """テーマIDからテーマ情報を取得"""
        try:
            with open('prompts_data.json', 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            # 全フェーズから該当テーマを検索
            for phase_name, phase_data in prompts_data.items():
                if theme_id in phase_data:
                    return phase_data[theme_id]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
        
        return None
    
    def get_phase_for_theme(self, theme_id):
        """テーマIDからフェーズ名を取得"""
        phase_mapping = {
            'A': 'phase_1', 'B': 'phase_1',
            '1': 'phase_2', '2': 'phase_2', '3': 'phase_2', '4': 'phase_2',
            '5': 'phase_3', '6': 'phase_3', '7': 'phase_3',
            '8': 'phase_4', '9': 'phase_4', '10': 'phase_4', '11': 'phase_4', '12': 'phase_4',
            '13': 'phase_5', '14': 'phase_5', '15': 'phase_5',
            '16': 'phase_6', '17': 'phase_6', '18': 'phase_6', '19': 'phase_6', '20': 'phase_6',
            '21': 'phase_6', '22': 'phase_6', '23': 'phase_6', '24': 'phase_6', '25': 'phase_6', '26': 'phase_6',
            '27': 'phase_7', '28': 'phase_7', '29': 'phase_7', '30': 'phase_7', '31': 'phase_7', '32': 'phase_7',
            '33': 'phase_8', '34': 'phase_8', '35': 'phase_8',
            'Z': 'final_phase'
        }
        return phase_mapping.get(theme_id, 'phase_1')

    def quality_check_mode(self, config_data):
        """品質チェックモード"""
        print("\n品質チェックを実行します...")
        
        from pathlib import Path
        from src.utils.validators import QualityChecker
        
        quality_checker = QualityChecker()
        output_dir = Path('outputs') / config_data['project_name']
        
        if not output_dir.exists():
            print("❌ まだレポートが生成されていません。")
            return
        
        # すべてのレポートをチェック
        all_reports = list(output_dir.rglob('*.md'))
        issues_found = False
        
        for report_path in all_reports:
            if '00_全体戦略サマリー' not in str(report_path):
                result = quality_checker.check_report(report_path)
                if not result['passed']:
                    issues_found = True
                    print(f"\n⚠️  {report_path.name}")
                    for issue in result['issues']:
                        print(f"   - {issue}")
        
        if not issues_found:
            print("\n✅ すべてのレポートが品質基準を満たしています。")
        else:
            print("\n品質改善が必要なレポートがあります。")
            retry = input("再実行しますか？ (y/n): ")
            if retry.lower() == 'y':
                # TODO: 品質基準を満たさないレポートのみ再実行
                print("再実行機能は開発中です。")

    def run(self):
        """メイン実行"""
        self.interactive_mode()

if __name__ == "__main__":
    app = BSRSMain()
    app.run() 