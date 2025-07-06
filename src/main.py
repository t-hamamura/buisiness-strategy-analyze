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
            
            # 既存のテーマ・フェーズ選択処理
            self.select_theme_and_phase()
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
        """テーマ選択モード"""
        print("\n実行するテーマを選択してください:")
        
        # フェーズ設定を読み込み
        import json
        with open('config/phase_config.json', 'r', encoding='utf-8') as f:
            all_phases = json.load(f)
        
        # すべてのテーマをリスト化
        theme_list = []
        for phase_name, phase_data in all_phases.items():
            for theme_id, theme_info in phase_data['themes'].items():
                theme_list.append({
                    'phase': phase_name,
                    'theme_id': theme_id,
                    'name': theme_info['name'],
                    'display': f"{theme_id}: {theme_info['name']} ({phase_data['name']})"
                })
        
        # テーマを表示
        for idx, theme in enumerate(theme_list, 1):
            print(f"{idx}. {theme['display']}")
        
        choice = input(f"\n選択 (1-{len(theme_list)}): ")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(theme_list):
                selected = theme_list[idx]
                # 単一テーマの実行
                self.controller.run_single_theme(
                    config_data, 
                    selected['phase'], 
                    selected['theme_id']
                )
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")

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