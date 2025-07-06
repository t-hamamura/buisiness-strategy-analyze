"""
Cursor Integration Helper - Cursor連携ヘルパー
"""
from pathlib import Path
import re
import json

class CursorIntegration:
    def __init__(self):
        self.temp_dir = Path('temp')
        self.temp_dir.mkdir(exist_ok=True)
    
    def format_prompt_for_cursor(self, base_prompt, config_data):
        """Cursor用にプロンプトをフォーマット"""
        web_search_instruction = """
【Web検索の活用方法】
1. 検索ボタンをクリックしてWeb検索を有効化
2. 以下のキーワードで検索：
   - {company_name} {industry} 市場分析 2024
   - {competitors} 戦略 事例
   - {target_market} トレンド 統計
3. 信頼できる情報源を優先（公式サイト、業界レポート、政府統計など）
""".format(
            company_name=config_data.get('company_name', ''),
            industry=config_data.get('industry', ''),
            competitors=' '.join(config_data.get('competitors', [])),
            target_market=config_data.get('target_market', '')
        )
        
        return base_prompt + "\n\n" + web_search_instruction
    
    def parse_cursor_response(self, response_text):
        """Cursor応答をパース"""
        # 引用の抽出
        citations = re.findall(r'\[(\d+)\]\s*(https?://[^\s]+)', response_text)
        
        # セクションの抽出
        sections = {}
        current_section = None
        current_content = []
        
        for line in response_text.split('\n'):
            if line.startswith('#'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip('# ').strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return {
            'full_text': response_text,
            'sections': sections,
            'citations': citations
        }
    
    def save_intermediate_result(self, phase, theme, step, content):
        """中間結果を保存"""
        filename = self.temp_dir / f"{phase}_{theme}_step{step}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return filename 