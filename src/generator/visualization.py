"""
Visualization Generator - 図表生成
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from pathlib import Path
import numpy as np

class VisualizationGenerator:
    def __init__(self):
        # 日本語フォントの設定
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo']
        plt.rcParams['axes.unicode_minus'] = False
        
        self.output_dir = Path('outputs/charts')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_swot_analysis(self, data, filename="swot_analysis.png"):
        """SWOT分析図の作成"""
        fig, ax = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('SWOT分析', fontsize=20, fontweight='bold')
        
        # 各象限の設定
        quadrants = [
            ('強み (Strengths)', data.get('strengths', []), 'lightblue'),
            ('弱み (Weaknesses)', data.get('weaknesses', []), 'lightcoral'),
            ('機会 (Opportunities)', data.get('opportunities', []), 'lightgreen'),
            ('脅威 (Threats)', data.get('threats', []), 'lightyellow')
        ]
        
        for idx, (title, items, color) in enumerate(quadrants):
            row = idx // 2
            col = idx % 2
            ax[row, col].set_title(title, fontsize=16, fontweight='bold')
            ax[row, col].set_facecolor(color)
            
            # 項目を追加
            y_pos = 0.9
            for item in items[:5]:  # 最大5項目
                ax[row, col].text(0.05, y_pos, f'• {item}', 
                                transform=ax[row, col].transAxes,
                                fontsize=12, va='top')
                y_pos -= 0.18
            
            ax[row, col].set_xlim(0, 1)
            ax[row, col].set_ylim(0, 1)
            ax[row, col].axis('off')
        
        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
    
    def create_competitor_map(self, data, filename="competitor_map.png"):
        """競合ポジショニングマップの作成"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # データの準備
        companies = data.get('companies', [])
        x_values = data.get('x_values', [])  # 例：価格
        y_values = data.get('y_values', [])  # 例：品質
        sizes = data.get('sizes', [100] * len(companies))  # 例：市場シェア
        
        # 散布図の作成
        scatter = ax.scatter(x_values, y_values, s=sizes, alpha=0.6, 
                           c=range(len(companies)), cmap='viridis')
        
        # 企業名のラベル
        for i, company in enumerate(companies):
            ax.annotate(company, (x_values[i], y_values[i]), 
                      xytext=(5, 5), textcoords='offset points')
        
        # 軸の設定
        ax.set_xlabel(data.get('x_label', '価格競争力'), fontsize=14)
        ax.set_ylabel(data.get('y_label', '品質・機能'), fontsize=14)
        ax.set_title('競合ポジショニングマップ', fontsize=18, fontweight='bold')
        
        # グリッドの追加
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
    
    def create_market_growth_chart(self, data, filename="market_growth.png"):
        """市場成長グラフの作成"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        years = data.get('years', list(range(2020, 2026)))
        values = data.get('values', [])
        
        # 折れ線グラフと面グラフ
        ax.plot(years, values, 'o-', linewidth=3, markersize=8, label='市場規模')
        ax.fill_between(years, values, alpha=0.3)
        
        # 成長率の表示
        for i in range(1, len(years)):
            growth_rate = ((values[i] - values[i-1]) / values[i-1]) * 100
            ax.text(years[i], values[i], f'+{growth_rate:.1f}%', 
                   ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('年度', fontsize=14)
        ax.set_ylabel('市場規模（億円）', fontsize=14)
        ax.set_title('市場成長予測', fontsize=18, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
    
    def create_strategy_timeline(self, data, filename="strategy_timeline.png"):
        """戦略実行タイムラインの作成"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        phases = data.get('phases', [])
        start_times = data.get('start_times', [])
        durations = data.get('durations', [])
        
        # ガントチャート風のタイムライン
        for i, (phase, start, duration) in enumerate(zip(phases, start_times, durations)):
            ax.barh(i, duration, left=start, height=0.6, 
                   alpha=0.8, label=phase)
            ax.text(start + duration/2, i, phase, 
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        ax.set_yticks(range(len(phases)))
        ax.set_yticklabels([])
        ax.set_xlabel('月', fontsize=14)
        ax.set_title('戦略実行タイムライン', fontsize=18, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
    
    def create_analysis_charts(self, theme_id, results):
        """全36テーマに対応した図表生成（雛形）"""
        charts = []
        chart_mapping = {
            'A': ['swot_analysis', 'vrio_framework'],
            'B': ['business_model_canvas', 'revenue_stream_analysis'],
            '1': ['market_size_chart', 'tam_sam_som_diagram'],
            '2': ['pestle_analysis_chart'],
            '3': ['competitor_positioning_map', '4p_comparison'],
            '4': ['technology_trend_radar'],
            '5': ['customer_segmentation_matrix'],
            '6': ['message_hierarchy_pyramid'],
            '7': ['customer_journey_map'],
            '8': ['hypothesis_validation_matrix'],
            '9': ['brand_identity_prism'],
            '10': ['gtm_strategy_canvas'],
            '11': ['ecosystem_map'],
            '12': ['localization_heatmap'],
            '13': ['growth_funnel', 'retention_curve'],
            '14': ['ltv_cac_dashboard'],
            '15': ['freemium_conversion_funnel'],
            '16': ['content_channel_matrix'],
            '17': ['creative_performance_dashboard'],
            '18': ['pr_timeline'],
            '19': ['media_mix_allocation'],
            '20': ['youtube_analytics_dashboard'],
            '21': ['instagram_engagement_metrics'],
            '22': ['twitter_analytics_dashboard'],
            '23': ['tiktok_performance_metrics'],
            '24': ['affiliate_network_map'],
            '25': ['influencer_impact_matrix'],
            '26': ['customer_success_journey'],
            '27': ['martech_stack_diagram'],
            '28': ['sales_enablement_framework'],
            '29': ['kpi_dashboard'],
            '30': ['org_structure_diagram'],
            '31': ['decision_flow_chart'],
            '32': ['learning_loop_diagram'],
            '33': ['esg_materiality_matrix'],
            '34': ['scenario_planning_matrix'],
            '35': ['crisis_response_flowchart'],
            'Z': ['integrated_strategy_map', 'executive_dashboard']
        }
        if theme_id in chart_mapping:
            for chart_type in chart_mapping[theme_id]:
                # サンプル: ファイル名だけ返す（実装は各メソッドで対応）
                charts.append(f"outputs/charts/{theme_id}_{chart_type}.png")
        return charts 