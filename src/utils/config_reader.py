"""
Config Reader - 設定ファイル読み込み
"""
import os
import re
import json
from pathlib import Path

class ConfigReader:
    def __init__(self):
        self.config_patterns = ['project_config.md', '*_config.md', 'research_config.md']
    
    def find_config_file(self):
        """設定ファイルを検索"""
        for pattern in self.config_patterns:
            files = list(Path('.').glob(pattern))
            if files:
                return files[0]
        return None
    
    def load_config(self, config_file):
        """設定ファイルを読み込んでパース"""
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config_data = {}
        
        # 基本情報の抽出
        config_data['project_name'] = self.extract_value(content, 'プロジェクト名')
        config_data['company_name'] = self.extract_value(content, '自社名')
        config_data['industry'] = self.extract_value(content, '業界')
        config_data['product_service'] = self.extract_value(content, '製品/サービスの概要')
        
        # 市場・競合情報
        config_data['target_market'] = self.extract_value(content, '対象市場')
        config_data['region'] = self.extract_value(content, '国・地域')
        competitors_str = self.extract_value(content, '競合企業')
        config_data['competitors'] = [c.strip() for c in competitors_str.split(',')]
        
        # ターゲット顧客
        config_data['target_customer'] = self.extract_value(content, 'ターゲット顧客セグメント')
        config_data['persona'] = self.extract_value(content, '顧客ペルソナ')
        
        # その他の設定
        config_data['objective'] = self.extract_value(content, '調査目的')
        config_data['timeline'] = self.extract_value(content, 'タイムライン')
        config_data['enable_web_search'] = True  # デフォルトで有効
        
        return config_data
    
    def extract_value(self, content, key):
        """設定値を抽出"""
        # パターン: - key: [値] または - key: 値
        pattern = rf'-\s*{key}:\s*\[?([^\[\]\n]+)\]?'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        return ''
    
    def validate_config(self, config_data):
        """設定の妥当性チェック"""
        required_fields = ['project_name', 'company_name', 'industry']
        missing_fields = []
        
        for field in required_fields:
            if not config_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"必須フィールドが不足しています: {', '.join(missing_fields)}")
        
        return True 