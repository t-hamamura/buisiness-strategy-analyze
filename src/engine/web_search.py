"""
Web Search Interface - Web検索機能
"""
import time
from typing import List, Dict

class WebSearchInterface:
    def __init__(self):
        self.search_count = 0
        self.max_searches_per_minute = 30
    
    def search_multiple(self, queries: List[str]) -> List[Dict]:
        """複数のクエリで検索を実行"""
        all_results = []
        
        for query in queries:
            results = self.search_single(query)
            all_results.extend(results)
            time.sleep(1)  # レート制限対策
        
        return all_results
    
    def search_single(self, query: str) -> List[Dict]:
        """単一クエリでの検索（Cursor内蔵検索を使用）"""
        print(f"🔎 検索中: {query}")
        
        # Cursor内蔵のWeb検索機能を使用
        search_instruction = f"""
以下のクエリでWeb検索を実行し、関連性の高い情報を収集してください：
クエリ: {query}

以下の形式で結果を返してください：
- タイトル
- URL
- 要約（100文字程度）
- 関連性スコア（1-10）

最低10件、最大15件の結果を返してください。
"""
        
        # Cursorの検索結果（擬似的な結果）
        results = [
            {
                'title': f'{query}に関する調査結果',
                'url': f'https://example.com/{query.replace(" ", "-")}',
                'snippet': f'{query}についての詳細な分析結果...',
                'relevance_score': 8
            }
        ]
        
        self.search_count += 1
        return results
    
    def extract_facts_from_results(self, search_results: List[Dict]) -> List[str]:
        """検索結果から重要な事実を抽出"""
        facts = []
        
        for result in search_results:
            if result.get('relevance_score', 0) >= 7:
                fact = f"- {result['title']}: {result['snippet']} (出典: {result['url']})"
                facts.append(fact)
        
        return facts 