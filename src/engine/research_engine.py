"""
Research Engine - 調査実行エンジン
"""
import os
import json
from pathlib import Path
from datetime import datetime
from src.engine.web_search import WebSearchInterface

class ResearchEngine:
    def __init__(self):
        self.web_search = WebSearchInterface()
        self.prompts_dir = Path('prompts')
    
    def execute_research(self, config_data, phase_name, theme_id, step, 
                        previous_results=None, theme_results=None):
        """調査の実行"""
        # プロンプトの読み込み
        prompt = self.load_prompt(phase_name, theme_id, step)
        
        # 変数の置換
        prompt = self.replace_variables(prompt, config_data)
        
        # 前の結果を含める
        if step > 1 and theme_results:
            prompt = self.add_previous_context(prompt, theme_results)
        
        if previous_results and step == 1:
            prompt = self.add_phase_context(prompt, previous_results)
        
        # Cursor AIに調査を実行させる
        print(f"\n🔍 以下のプロンプトで調査を実行します:")
        print("-" * 80)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 80)
        
        # ここでCursor AIのAuto機能を使用
        research_result = self.execute_with_cursor_ai(prompt)
        
        # Web検索で情報を補強
        if config_data.get('enable_web_search', True):
            search_queries = self.extract_search_queries(research_result)
            web_results = self.web_search.search_multiple(search_queries)
            research_result = self.enhance_with_web_results(research_result, web_results)
        
        return {
            'theme_id': theme_id,
            'step': step,
            'prompt': prompt,
            'result': research_result,
            'timestamp': datetime.now().isoformat(),
            'sources': self.extract_sources(research_result)
        }
    
    def load_prompt(self, phase_name, theme_id, step):
        """プロンプトファイルの読み込み"""
        prompt_file = self.prompts_dir / phase_name / f"{theme_id}_step{step}.md"
        
        if not prompt_file.exists():
            # デフォルトプロンプトを生成
            return self.generate_default_prompt(phase_name, theme_id, step)
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_default_prompt(self, phase_name, theme_id, step):
        """デフォルトプロンプトの生成"""
        prompts_map = {
            'step1': """# 命令書：フェーズ{phase} - {theme} - 現状分析

あなたは、{role}です。
{company}の{theme}について、以下の観点から現状を分析してください：

1. 現状の把握と課題の特定
2. 業界ベストプラクティスとの比較
3. 定量的・定性的データの収集と分析

必ず以下を含めてください：
- 最低10個以上の信頼できる情報源からの引用
- 具体的な数値やデータ
- 視覚的な図表（可能な場合）

Web検索を活用して最新の情報を収集し、深い分析を行ってください。
""",
            'step2': """# 命令書：フェーズ{phase} - {theme} - 戦略立案

前のステップの分析結果を踏まえ、以下を策定してください：

1. 戦略オプションの検討（最低3案）
2. 各オプションの評価（メリット・デメリット・実現可能性）
3. 推奨戦略の選定と根拠

参照すべき前の分析結果：
{previous_context}

必ず根拠となるデータや事例を示してください。
""",
            'step3': """# 命令書：フェーズ{phase} - {theme} - 実行計画

選定された戦略を実現するための具体的な実行計画を策定してください：

1. アクションプランの詳細（タスク・担当・期限）
2. 必要なリソース（人材・予算・ツール）
3. KPIと成功指標の設定
4. リスクと対策

実行可能性を重視し、具体的で測定可能な計画を作成してください。
"""
        }
        
        step_key = f'step{step}'
        template = prompts_map.get(step_key, prompts_map['step1'])
        
        return template.format(
            phase=phase_name,
            theme=theme_id,
            role=self.get_role_for_theme(theme_id),
            company="{company}"  # 後で置換
        )
    
    def replace_variables(self, prompt, config_data):
        """プロンプト内の変数を置換"""
        replacements = {
            '[自社名]': config_data.get('company_name', ''),
            '{company}': config_data.get('company_name', ''),
            '[業界]': config_data.get('industry', ''),
            '[製品/サービス]': config_data.get('product_service', ''),
            '[対象市場]': config_data.get('target_market', ''),
            '[競合企業]': ', '.join(config_data.get('competitors', [])),
            '[ターゲット顧客]': config_data.get('target_customer', ''),
        }
        
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        
        return prompt
    
    def execute_with_cursor_ai(self, prompt):
        """Cursor AIでの実行（実際の実装ではCursorのAPIを使用）"""
        # この部分は実際のCursor環境で実行される
        instruction = f"""
以下の調査プロンプトを実行し、詳細なレポートを作成してください。
Web検索を積極的に活用し、最新かつ信頼性の高い情報を収集してください。

{prompt}

出力形式：
- マークダウン形式
- 明確な見出し構造
- 引用と出典の明記（脚注形式）
- 可能な限り図表を含める
"""
        
        # Cursor AIの応答を待つ（この部分は擬似コード）
        print("\n⏳ Cursor AIが調査を実行中... (Autoモードで実行)")
        print("💡 ヒント: Web検索を活用して深い分析を行います")
        
        # 実際にはCursorのAuto機能が動作
        result = "[Cursor AIの実行結果がここに入ります]"
        
        return result
    
    def extract_search_queries(self, research_result):
        """調査結果から追加検索クエリを抽出"""
        # 簡易的な実装（実際にはより高度な抽出ロジックを使用）
        queries = []
        
        # キーワード抽出ロジック
        keywords = ['市場規模', 'シェア', 'トレンド', '事例', '統計']
        for keyword in keywords:
            if keyword in research_result:
                queries.append(f"{keyword} 2024 日本")
        
        return queries[:5]  # 最大5クエリ
    
    def enhance_with_web_results(self, research_result, web_results):
        """Web検索結果で調査結果を補強"""
        # 検索結果を調査結果に統合
        enhanced_result = research_result
        
        if web_results:
            enhanced_result += "\n\n## 追加のWeb検索結果\n\n"
            for idx, result in enumerate(web_results, 1):
                enhanced_result += f"### {idx}. {result['title']}\n"
                enhanced_result += f"URL: {result['url']}\n"
                enhanced_result += f"{result['snippet']}\n\n"
        
        return enhanced_result
    
    def extract_sources(self, research_result):
        """調査結果から出典を抽出"""
        sources = []
        # 簡易的な出典抽出（実際にはより高度なパーシングを使用）
        lines = research_result.split('\n')
        for line in lines:
            if 'http' in line or '出典:' in line or 'Source:' in line:
                sources.append(line.strip())
        
        return sources
    
    def get_role_for_theme(self, theme_id):
        """テーマに応じた役割を返す"""
        roles = {
            'A': 'マッキンゼーの経営コンサルタント',
            'B': 'ビジネスモデルイノベーションの専門家',
            '1': 'IDCのシニアマーケットアナリスト',
            '2': 'デロイトのリスク管理コンサルタント',
            # ... 他のテーマの役割
        }
        return roles.get(theme_id, '戦略コンサルタント')

    def add_previous_context(self, prompt, theme_results):
        """前のステップの結果をプロンプトに追加"""
        if not theme_results:
            return prompt
        
        context = "\n\n## 前のステップの分析結果\n\n"
        for idx, result in enumerate(theme_results, 1):
            context += f"### ステップ{idx}の要約\n"
            # 結果の最初の500文字を抽出
            summary = result.get('result', '')[:500]
            context += f"{summary}...\n\n"
        
        return prompt.replace('{previous_context}', context)

    def add_phase_context(self, prompt, previous_results):
        """前フェーズの結果をプロンプトに追加"""
        if not previous_results:
            return prompt
        
        context = "\n\n## 関連する前フェーズの分析結果\n\n"
        # 前フェーズの要約を追加（簡易版）
        context += "前フェーズの分析により、以下の重要な知見が得られています：\n"
        context += "- [前フェーズの重要な発見]\n"
        context += "- [関連する戦略的示唆]\n\n"
        
        return prompt + context 