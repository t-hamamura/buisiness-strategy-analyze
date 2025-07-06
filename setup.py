"""
Business Strategy Research System Setup Script
"""
import os
import json
import shutil
from pathlib import Path

class SystemSetup:
    def __init__(self):
        self.root_dir = Path.cwd()
        
    def create_directories(self):
        """必要なディレクトリ構造を作成"""
        directories = [
            'config', 'src/controller', 'src/engine', 
            'src/generator', 'src/utils', 'prompts',
            'templates', 'outputs', 'tests'
        ]
        # フェーズごとのプロンプトディレクトリ
        for i in range(1, 9):
            directories.append(f'prompts/phase_{i}')
        directories.append('prompts/final_phase')
        
        for dir_path in directories:
            Path(self.root_dir / dir_path).mkdir(parents=True, exist_ok=True)
            # __init__.pyの作成
            if 'src' in dir_path or 'tests' in dir_path:
                (self.root_dir / dir_path / '__init__.py').touch()
    
    def create_config_files(self):
        """設定ファイルの作成"""
        # system_config.json
        system_config = {
            "version": "1.0.0",
            "research_phases": 8,
            "themes_per_phase": {
                "phase_1": 2,
                "phase_2": 4,
                "phase_3": 3,
                "phase_4": 5,
                "phase_5": 3,
                "phase_6": 11,
                "phase_7": 6,
                "phase_8": 3,
                "final_phase": 1
            },
            "output_format": "markdown",
            "web_search": {
                "enabled": True,
                "max_results": 15,
                "timeout": 30
            },
            "quality_check": {
                "min_sources": 10,
                "min_word_count": 3000,
                "required_sections": ["概要", "詳細分析", "戦略提言", "参考文献"]
            }
        }
        
        with open(self.root_dir / 'config' / 'system_config.json', 'w', encoding='utf-8') as f:
            json.dump(system_config, f, ensure_ascii=False, indent=2)
    
    def create_template_files(self):
        """テンプレートファイルの作成"""
        research_config_template = """# 事業調査設定ファイル

## 1. プロジェクト全体定義
- プロジェクト名: [プロジェクト名を入力]
- 調査目的: [調査の目的を入力]
- 最終的なアウトプット: [期待する成果物を入力]
- タイムライン: [完了予定日を入力]

## 2. 自社・製品/サービス定義
- 自社名: [企業名を入力]
- 業界: [業界を入力]
- 製品/サービスの概要: [30秒で説明できる概要を入力]
- 創業年: [創業年を入力]
- 事業ステージ: [シード/シリーズA/成長期など]
- 従業員規模: [人数を入力]

## 3. 市場・競合環境定義
- 対象市場: [市場名を入力]
- 国・地域: [対象地域を入力]
- 競合企業: [競合A社], [競合B社], [競合C社]
- 市場規模（推定）: [金額を入力]

## 4. ターゲット顧客定義
- ターゲット顧客セグメント: [セグメントを入力]
- 分析対象とする主要な顧客ペルソナ: [ペルソナ詳細を入力]

## 5. 調査スコープ
- 重点調査エリア: [特に深掘りしたい領域]
- 除外事項: [調査対象外とする領域]
- 時間軸: [短期(1年)/中期(3年)/長期(5年)]

## 6. その他
- 参考にしたい企業事例: [企業名]
- 既存の調査レポート: [ある場合はファイル名]
- 特記事項: [その他の重要事項]
"""
        
        with open(self.root_dir / 'templates' / 'research_config_template.md', 
                  'w', encoding='utf-8') as f:
            f.write(research_config_template)
    
    def run(self):
        """セットアップの実行"""
        print("🚀 Business Strategy Research System セットアップを開始します...")
        self.create_directories()
        print("✅ ディレクトリ構造を作成しました")
        self.create_config_files()
        print("✅ 設定ファイルを作成しました")
        self.create_template_files()
        print("✅ テンプレートファイルを作成しました")
        
        # プロンプトファイルの自動生成を追加
        print("📝 プロンプトファイルを生成中...")
        from create_prompts import PromptCreator
        prompt_creator = PromptCreator()
        prompt_creator.create_all_prompts()
        
        print("✨ セットアップが完了しました！")

if __name__ == "__main__":
    setup = SystemSetup()
    setup.run() 