"""
Quality Checker - レポート品質チェック
"""
import re
from pathlib import Path

class QualityChecker:
    def __init__(self):
        self.min_word_count = 3000
        self.min_sources = 10
        self.required_sections = ['現状分析', '戦略提言', '実行計画', '参考文献']
    
    def check_report(self, report_path):
        """レポートの品質チェック"""
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {
            'passed': True,
            'score': 100,
            'issues': []
        }
        
        # 文字数チェック
        word_count = len(content)
        if word_count < self.min_word_count:
            results['issues'].append(f"文字数不足: {word_count}文字 (最低{self.min_word_count}文字)")
            results['score'] -= 20
        
        # 必須セクションチェック
        for section in self.required_sections:
            if section not in content:
                results['issues'].append(f"必須セクション不足: {section}")
                results['score'] -= 10
        
        # 参考文献数チェック
        references = re.findall(r'\d+\.\s+.*https?://', content)
        if len(references) < self.min_sources:
            results['issues'].append(f"参考文献不足: {len(references)}件 (最低{self.min_sources}件)")
            results['score'] -= 15
        
        # 図表の存在チェック
        has_charts = '![' in content or '|' in content
        if not has_charts:
            results['issues'].append("図表が含まれていません")
            results['score'] -= 10
        
        # 合格判定
        results['passed'] = results['score'] >= 70
        
        return results 