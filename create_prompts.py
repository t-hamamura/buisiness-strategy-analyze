#!/usr/bin/env python
"""
PDFベースのプロンプト生成スクリプト
"""
import json
from pathlib import Path

class PDFBasedPromptCreator:
    def __init__(self):
        self.prompts_base = Path('prompts')
        self.load_prompts_data()
        
    def load_prompts_data(self):
        """PDFから抽出した全36テーマのプロンプトデータを読み込み"""
        try:
            with open('prompts_data.json', 'r', encoding='utf-8') as f:
                self.prompts_data = json.load(f)
        except FileNotFoundError:
            print("❌ prompts_data.json が見つかりません")
            print("💡 extract_pdf_prompts.py を先に実行してください")
            return
        
        print(f"✅ {len(self.prompts_data)} フェーズのプロンプトデータを読み込みました")
    
    def create_prompt_files(self):
        """全36テーマ（A, B, 1-35, Z）のプロンプトファイルを生成"""
        print("PDFベースのプロンプト生成を開始...")
        
        # フェーズごとに処理
        phase_mapping = {
            'phase_1': ['A', 'B'],
            'phase_2': ['1', '2', '3', '4'],
            'phase_3': ['5', '6', '7'],
            'phase_4': ['8', '9', '10', '11', '12'],
            'phase_5': ['13', '14', '15'],
            'phase_6': ['16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26'],
            'phase_7': ['27', '28', '29', '30', '31', '32'],
            'phase_8': ['33', '34', '35'],
            'final_phase': ['Z']
        }
        
        total_files = 0
        
        for phase_name, theme_ids in phase_mapping.items():
            if phase_name not in self.prompts_data:
                print(f"⚠️  {phase_name} のデータが見つかりません")
                continue
                
            phase_dir = self.prompts_base / phase_name
            phase_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📁 {self.get_phase_name_jp(phase_name)} を処理中...")
            
            for theme_id in theme_ids:
                if theme_id in self.prompts_data[phase_name]:
                    theme_data = self.prompts_data[phase_name][theme_id]
                    files_created = self.create_theme_prompts(phase_name, theme_id, theme_data)
                    total_files += files_created
                else:
                    print(f"  ⚠️  テーマ {theme_id} のデータが見つかりません")
        
        print(f"\n✅ 合計 {total_files} 個のプロンプトファイルを生成しました")
    
    def create_theme_prompts(self, phase_name, theme_id, theme_data):
        """各テーマの3ステップ分のプロンプトを生成"""
        files_created = 0
        
        for step_num in ['1', '2', '3']:
            if step_num in theme_data.get('steps', {}):
                prompt_file = self.prompts_base / phase_name / f"{theme_id}_step{step_num}.md"
                content = self.generate_prompt_content(phase_name, theme_id, theme_data, step_num)
                
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  ✓ {phase_name}/{theme_id}_step{step_num}.md を生成")
                files_created += 1
        
        return files_created
    
    def generate_prompt_content(self, phase_name, theme_id, theme_data, step_num):
        """PDFの内容に基づいてプロンプトコンテンツを生成"""
        step_data = theme_data['steps'][step_num]
        
        if step_num == '1':
            # ステップ1のプロンプト
            content = f"""# 命令書：{self.get_phase_name_jp(phase_name)} - {theme_data['name']} - ステップ1：{step_data['title']}

あなたは、{step_data.get('role', '専門コンサルタント')}です。

## 主要な問い
{theme_data['main_question']}

## 背景と目的
{theme_data['description']}

## 調査指示
クライアントである{' / '.join(theme_data.get('variables', ['[自社名]']))}について、以下の観点から徹底的な分析を行ってください：

### 1. 現状の詳細把握
- 定量的・定性的データの収集と分析
- 業界標準やベストプラクティスとの比較
- 強みと弱みの明確な特定

### 2. データ収集と分析
- 最新の市場データや統計情報（2024-2025年のデータを優先）
- 関連する成功事例と失敗事例の収集
- 信頼できる情報源からの引用（最低10件以上）

### 3. 課題と機会の特定
- 現状の問題点や改善余地の明確化
- 潜在的なリスクと機会の洗い出し
- 競合他社との差異分析

## 必須成果物
"""
            # 成果物リストを追加
            for deliverable in theme_data.get('deliverables', []):
                content += f"- {deliverable}\n"
            
            content += """
## 注意事項
- 必ずWeb検索を積極的に活用し、最新情報を含めてください
- 具体的な数値データと出典を明記してください
- 図表や視覚的な表現を活用してください
- 分析結果は客観的で根拠のある内容にしてください
"""
        
        elif step_num == '2':
            # ステップ2のプロンプト（前ステップ参照）
            content = f"""# 命令書：{self.get_phase_name_jp(phase_name)} - {theme_data['name']} - ステップ2：{step_data['title']}

## 参照コンテキスト
### ▼▼▼ 以下に、ステップ1で生成されたレポートをそのまま貼り付けてください ▼▼▼

### ▲▲▲ ステップ1のレポートここまで ▲▲▲

## 前提条件
ステップ1の分析結果を踏まえて、戦略的な提言を行います。

## 戦略立案の指示
1. **戦略オプションの検討**
   - 最低3つの戦略案を提示
   - 各案のメリット・デメリット・実現可能性を評価
   - 投資対効果（ROI）の見込み

2. **推奨戦略の選定**
   - 最も効果的な戦略の選定と根拠
   - 期待される成果と達成時期
   - 必要なリソースと前提条件

3. **リスク評価**
   - 実施上のリスクと対策
   - 代替案の検討
   - 成功確率の評価

## 必須成果物
"""
            # 成果物リストを追加（ステップ2用に調整）
            for deliverable in theme_data.get('deliverables', []):
                if '戦略' in deliverable or 'プラン' in deliverable or '案' in deliverable:
                    content += f"- {deliverable}\n"
            
            content += """
## 注意事項
- ステップ1の分析結果を基に、具体的で実行可能な戦略を提案してください
- 定量的な根拠と予測を含めてください
- 優先順位を明確にしてください
"""
        
        else:  # step_num == '3'
            # ステップ3のプロンプト
            content = f"""# 命令書：{self.get_phase_name_jp(phase_name)} - {theme_data['name']} - ステップ3：{step_data['title']}

## 参照コンテキスト
### ▼▼▼ 以下に、ステップ2で生成されたレポートをそのまま貼り付けてください ▼▼▼

### ▲▲▲ ステップ2のレポートここまで ▲▲▲

## 実行計画の策定指示
選定された戦略を実現するための具体的な計画を立案してください：

1. **アクションプラン**
   - 具体的なタスクとマイルストーン
   - 責任者と実行チーム
   - タイムラインとデッドライン

2. **必要リソース**
   - 人材（スキル要件、人数）
   - 予算（初期投資、運用コスト）
   - ツールやシステム

3. **成功指標（KPI）**
   - 測定可能な目標値
   - モニタリング方法と頻度
   - 評価基準と修正トリガー

4. **実装上の注意点**
   - 想定される障害と対策
   - ステークホルダーとのコミュニケーション計画
   - 変更管理プロセス

## 必須成果物
"""
            # 成果物リストを追加（ステップ3用に調整）
            for deliverable in theme_data.get('deliverables', []):
                if '実行' in deliverable or '計画' in deliverable or 'アクション' in deliverable:
                    content += f"- {deliverable}\n"
            
            content += """
## 注意事項
- 具体的で測定可能なアクションプランを作成してください
- 実現可能性を重視してください
- リスクと対策を明確にしてください
"""
        
        return content
    
    def get_phase_name_jp(self, phase_name):
        """フェーズ名の日本語変換"""
        phase_names = {
            'phase_1': 'フェーズⅠ：内部環境分析と事業モデル評価',
            'phase_2': 'フェーズⅡ：外部環境分析と事業機会の特定',
            'phase_3': 'フェーズⅢ：ターゲット顧客とインサイトの解明',
            'phase_4': 'フェーズⅣ：提供価値と市場投入（GTM）戦略',
            'phase_5': 'フェーズⅤ：グロース戦略と収益性分析',
            'phase_6': 'フェーズⅥ：マーケティング・コミュニケーション戦略',
            'phase_7': 'フェーズⅦ：戦略実行を支える組織と基盤',
            'phase_8': 'フェーズⅧ：持続可能性とリスクマネジメント',
            'final_phase': '最終フェーズ：全体戦略の統合と提言'
        }
        return phase_names.get(phase_name, phase_name)

def main():
    """メイン処理"""
    print("PDFベースのプロンプト生成を開始します...")
    
    creator = PDFBasedPromptCreator()
    creator.create_prompt_files()
    
    print("\n🎉 プロンプト生成が完了しました！")
    print("📁 生成されたファイルは prompts/ ディレクトリに保存されています")

if __name__ == "__main__":
    main() 