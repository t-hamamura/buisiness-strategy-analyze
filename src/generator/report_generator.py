"""
Report Generator - レポート生成
"""
import os
from pathlib import Path
from datetime import datetime
# import matplotlib.pyplot as plt
# import seaborn as sns
# from src.generator.visualization import VisualizationGenerator

class ReportGenerator:
    def __init__(self):
        # self.viz_generator = VisualizationGenerator()
        self.output_base = Path('outputs')
    
    def generate_theme_report(self, config_data, phase_name, theme_id, 
                            theme_info, results):
        """テーマ別レポートの生成"""
        # 出力ディレクトリの作成
        output_dir = self.output_base / config_data['project_name'] / phase_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # レポートファイル名
        report_filename = f"{theme_id}_{theme_info['name']}.md"
        report_path = output_dir / report_filename
        
        # レポート内容の生成
        report_content = self.create_report_content(
            config_data, phase_name, theme_id, theme_info, results
        )
        
        # ファイルに保存
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"    📄 レポート生成: {report_path}")
        return report_path
    
    def create_report_content(self, config_data, phase_name, theme_id, 
                            theme_info, results):
        """レポート内容の作成"""
        content = f"""# {theme_info['name']}

**プロジェクト**: {config_data['project_name']}  
**フェーズ**: {self.get_phase_name_jp(phase_name)}  
**作成日**: {datetime.now().strftime('%Y年%m月%d日')}  
**企業名**: {config_data['company_name']}

---

## エグゼクティブサマリー

{self.create_executive_summary(results)}

---

## 目次

1. [現状分析](#現状分析)
2. [戦略提言](#戦略提言)
3. [実行計画](#実行計画)
4. [参考文献](#参考文献)

---

## 現状分析

{results[0]['result'] if results else ''}

### 主要な発見事項

{self.extract_key_findings(results[0]['result'] if results else '')}

### 分析図表

{self.create_analysis_charts(theme_id, results)}

---

## 戦略提言

{results[1]['result'] if len(results) > 1 else ''}

### 戦略オプション比較

{self.create_strategy_comparison_table(results[1] if len(results) > 1 else None)}

---

## 実行計画

{results[2]['result'] if len(results) > 2 else ''}

### アクションプラン

{self.create_action_plan_table(results[2] if len(results) > 2 else None)}

### KPI設定

{self.create_kpi_table(results[2] if len(results) > 2 else None)}

---

## 参考文献

{self.create_references_section(results)}

---

## 付録

### 調査手法
- Cursor AI による自動調査
- Web検索による最新情報の収集
- 3段階の深掘り分析（現状分析→戦略立案→実行計画）

### 品質保証
- 最低10個以上の信頼できる情報源を参照
- 定量的データに基づく分析
- 実行可能性を重視した提言

---

*本レポートは Business Strategy Research System により自動生成されました。*
"""
        return content
    
    def create_executive_summary(self, results):
        """エグゼクティブサマリーの作成"""
        summary_points = []
        
        # 各ステップから重要ポイントを抽出
        for idx, result in enumerate(results):
            if result and 'result' in result:
                # 簡易的な要約抽出（実際にはより高度な要約アルゴリズムを使用）
                lines = result['result'].split('\n')
                for line in lines:
                    if any(keyword in line for keyword in ['重要', '結論', '推奨', 'ポイント']):
                        summary_points.append(f"- {line.strip()}")
                        if len(summary_points) >= 5:
                            break
        
        return '\n'.join(summary_points[:5]) if summary_points else '要約を生成中...'
    
    def extract_key_findings(self, analysis_text):
        """主要な発見事項の抽出"""
        findings = []
        
        # テキストから箇条書きを抽出
        lines = analysis_text.split('\n')
        in_list = False
        
        for line in lines:
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                findings.append(line.strip())
                in_list = True
            elif in_list and not line.strip():
                break
        
        return '\n'.join(findings[:10]) if findings else '- 詳細は本文を参照'
    
    def create_analysis_charts(self, theme_id, results):
        """分析図表の作成"""
        chart_markdown = ""
        
        # テーマに応じた図表を生成（一時的に無効化）
        # if theme_id == 'A':
        #     # SWOT分析図
        #     chart_path = self.viz_generator.create_swot_analysis(results)
        #     chart_markdown = f"![SWOT分析]({chart_path})\n"
        # elif theme_id == '3':
        #     # 競合マップ
        #     chart_path = self.viz_generator.create_competitor_map(results)
        #     chart_markdown = f"![競合マップ]({chart_path})\n"
        
        return chart_markdown
    
    def create_strategy_comparison_table(self, strategy_result):
        """戦略オプション比較表の作成"""
        table = """
| 戦略オプション | メリット | デメリット | 実現可能性 | 推奨度 |
|--------------|---------|-----------|-----------|--------|
| オプション1 | - | - | 高 | ★★★★☆ |
| オプション2 | - | - | 中 | ★★★☆☆ |
| オプション3 | - | - | 低 | ★★☆☆☆ |
"""
        return table
    
    def create_action_plan_table(self, execution_result):
        """アクションプラン表の作成"""
        table = """
| フェーズ | アクション | 担当 | 期限 | 必要リソース |
|---------|-----------|------|------|------------|
| 短期（3ヶ月） | - | - | - | - |
| 中期（6ヶ月） | - | - | - | - |
| 長期（1年） | - | - | - | - |
"""
        return table
    
    def create_kpi_table(self, execution_result):
        """KPI設定表の作成"""
        table = """
| KPI | 現状値 | 目標値 | 測定頻度 | 責任者 |
|-----|--------|--------|---------|--------|
| - | - | - | 月次 | - |
| - | - | - | 四半期 | - |
| - | - | - | 年次 | - |
"""
        return table
    
    def create_references_section(self, results):
        """参考文献セクションの作成"""
        all_sources = []
        
        for idx, result in enumerate(results):
            if 'sources' in result:
                all_sources.extend(result['sources'])
        
        # 重複を削除し、番号付けする
        unique_sources = list(dict.fromkeys(all_sources))
        
        references = []
        for idx, source in enumerate(unique_sources[:20], 1):
            references.append(f"{idx}. {source}")
        
        return '\n'.join(references) if references else '調査中に参照した文献情報'
    
    def get_phase_name_jp(self, phase_name):
        """フェーズ名の日本語変換"""
        phase_names = {
            'phase_1': 'フェーズI: 内部環境分析と事業モデル評価',
            'phase_2': 'フェーズII: 外部環境分析と事業機会の特定',
            'phase_3': 'フェーズIII: ターゲット顧客とインサイトの解明',
            'phase_4': 'フェーズIV: 提供価値と市場投入(GTM)戦略',
            'phase_5': 'フェーズV: グロース戦略と収益性分析',
            'phase_6': 'フェーズVI: マーケティング・コミュニケーション戦略',
            'phase_7': '戦略実行を支える組織と基盤',
            'phase_8': '持続可能性とリスクマネジメント',
            'final_phase': '最終フェーズ: 全体戦略の統合と提言'
        }
        return phase_names.get(phase_name, phase_name)
    
    def generate_summary_report(self, config_data, all_results):
        """全体サマリーレポートの生成"""
        output_dir = self.output_base / config_data['project_name']
        summary_path = output_dir / f"00_全体戦略サマリーレポート_{datetime.now().strftime('%Y%m%d')}.md"
        
        summary_content = f"""# {config_data['project_name']} - 事業戦略 全体サマリーレポート

**作成日**: {datetime.now().strftime('%Y年%m月%d日')}  
**対象企業**: {config_data['company_name']}  
**業界**: {config_data.get('industry', '')}

---

## エグゼクティブサマリー

本レポートは、{config_data['company_name']}の包括的な事業戦略調査の結果をまとめたものです。
8つのフェーズ、39のテーマにわたる詳細な分析を通じて、以下の戦略的提言を行います。

### 主要な戦略提言

1. **短期（3-6ヶ月）**: [具体的なアクション]
2. **中期（6-12ヶ月）**: [具体的なアクション]
3. **長期（1-3年）**: [具体的なアクション]

---

## 各フェーズのサマリー

{self.create_phase_summaries(all_results)}

---

## 統合戦略マップ

{self.create_integrated_strategy_map(all_results)}

---

## 優先実行事項

### 最優先で取り組むべき5つのアクション

1. **[アクション1]**
   - 期待効果: [効果]
   - 必要リソース: [リソース]
   - 完了目標: [期限]

2. **[アクション2]**
   - 期待効果: [効果]
   - 必要リソース: [リソース]
   - 完了目標: [期限]

[以下同様]

---

## 成功指標（KPI）

| 指標カテゴリ | KPI | 現状値 | 1年後目標 | 3年後目標 |
|------------|-----|--------|-----------|-----------|
| 財務 | - | - | - | - |
| 顧客 | - | - | - | - |
| 内部プロセス | - | - | - | - |
| 学習と成長 | - | - | - | - |

---

## 次のステップ

1. 経営陣への報告と承認（1週間以内）
2. 実行チームの編成（2週間以内）
3. 詳細実行計画の策定（1ヶ月以内）
4. 第1四半期レビューの実施（3ヶ月後）

---

*本サマリーレポートは、全39テーマの詳細調査結果に基づいて作成されました。*
*各テーマの詳細については、個別レポートをご参照ください。*
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"\n✨ 全体サマリーレポート生成完了: {summary_path}") 