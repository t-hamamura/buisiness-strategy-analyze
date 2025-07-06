"""プロンプトファイルを生成するスクリプト"""
from pathlib import Path
import json

def create_prompt_files():
    """プロンプトファイルの生成"""
    prompts_base = Path('prompts')
    
    # phase_config.jsonを読み込み
    with open('config/phase_config.json', 'r', encoding='utf-8') as f:
        phase_config = json.load(f)
    
    # 各フェーズのプロンプトを生成
    for phase_name, phase_data in phase_config.items():
        phase_dir = prompts_base / phase_name
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        for theme_id, theme_info in phase_data['themes'].items():
            # 3段階のプロンプトを生成
            for step in range(1, 4):
                prompt_file = phase_dir / f"{theme_id}_step{step}.md"
                
                if step == 1:
                    content = f"""# 命令書：{phase_data['name']} - {theme_info['name']} - ステップ1：現状分析

## 主要な問い
{theme_info['main_question']}

## 調査指示
あなたは、この分野の専門家として、以下の観点から徹底的な現状分析を行ってください：

1. **現状の把握**
   - 現在の状況を定量的・定性的に分析
   - 業界標準やベストプラクティスとの比較
   - 強みと弱みの特定

2. **データ収集**
   - 最新の市場データや統計情報
   - 関連する事例や研究結果
   - 信頼できる情報源からの引用（最低10件）

3. **課題の特定**
   - 現状の問題点や改善余地
   - 潜在的なリスクや機会
   - 競合との差異分析

Web検索を積極的に活用し、2024年の最新情報を含めてください。
"""
                elif step == 2:
                    content = f"""# 命令書：{phase_data['name']} - {theme_info['name']} - ステップ2：戦略立案

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
"""
                else:  # step == 3
                    content = f"""# 命令書：{phase_data['name']} - {theme_info['name']} - ステップ3：実行計画

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
"""
                
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
    print("✅ プロンプトファイルの生成が完了しました")

if __name__ == "__main__":
    create_prompt_files() 