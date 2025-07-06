"""
Research Controller - 調査実行の制御
"""
import json
import time
from pathlib import Path
from datetime import datetime
from src.engine.research_engine import ResearchEngine
from src.generator.report_generator import ReportGenerator
from src.utils.validators import QualityChecker

class ResearchController:
    def __init__(self):
        self.research_engine = ResearchEngine()
        self.report_generator = ReportGenerator()
        self.quality_checker = QualityChecker()
        self.phase_results = {}
    
    def run_full_research(self, config_data):
        """全体調査の実行"""
        print(f"\n🚀 {config_data['project_name']} の全体調査を開始します...")
        start_time = time.time()
        
        # 全フェーズを順次実行
        phases = ["phase_1", "phase_2", "phase_3", "phase_4", 
                 "phase_5", "phase_6", "phase_7", "phase_8", "final_phase"]
        
        for phase in phases:
            print(f"\n📊 {phase} を実行中...")
            self.run_phase_research(config_data, phase)
            # フェーズ間で少し待機（API制限対策）
            time.sleep(2)
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 全体調査が完了しました！ (所要時間: {elapsed_time/60:.1f}分)")
        self.generate_summary_report(config_data)
    
    def run_phase_research(self, config_data, phase_name):
        """フェーズ単位での調査実行"""
        # フェーズ設定の読み込み
        phase_config = self.load_phase_config(phase_name)
        phase_results = {}
        
        for theme_id, theme_info in phase_config['themes'].items():
            print(f"\n  📝 {theme_id}: {theme_info['name']} を調査中...")
            
            # 3段階の深掘り調査
            theme_results = []
            for step in range(1, 4):
                # 前のフェーズの結果を参照
                previous_results = self.get_previous_results(phase_name, theme_id)
                
                # 調査実行
                result = self.research_engine.execute_research(
                    config_data=config_data,
                    phase_name=phase_name,
                    theme_id=theme_id,
                    step=step,
                    previous_results=previous_results,
                    theme_results=theme_results
                )
                
                theme_results.append(result)
                print(f"    ✓ ステップ {step}/3 完了")
                time.sleep(1)  # API制限対策
            
            # レポート生成
            report_path = self.report_generator.generate_theme_report(
                config_data=config_data,
                phase_name=phase_name,
                theme_id=theme_id,
                theme_info=theme_info,
                results=theme_results
            )
            
            # 品質チェック
            quality_result = self.quality_checker.check_report(report_path)
            if quality_result['passed']:
                print(f"    ✅ 品質チェック合格")
            else:
                print(f"    ⚠️  品質チェック要改善: {quality_result['issues']}")
            
            phase_results[theme_id] = {
                'results': theme_results,
                'report_path': report_path,
                'quality': quality_result
            }
        
        # フェーズ結果を保存
        self.phase_results[phase_name] = phase_results
        self.save_phase_results(config_data, phase_name, phase_results)
    
    def get_previous_results(self, current_phase, theme_id):
        """前フェーズの結果を取得"""
        # フェーズ番号を取得
        if current_phase == "final_phase":
            # 最終フェーズは全フェーズの結果を参照
            return self.phase_results
        
        phase_num = int(current_phase.split('_')[1])
        if phase_num == 1:
            return None
        
        # 前フェーズの結果を返す
        previous_phase = f"phase_{phase_num - 1}"
        return self.phase_results.get(previous_phase, None)
    
    def load_phase_config(self, phase_name):
        """フェーズ設定の読み込み"""
        config_path = Path('config') / 'phase_config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            all_phases = json.load(f)
        return all_phases.get(phase_name, {})
    
    def save_phase_results(self, config_data, phase_name, results):
        """フェーズ結果の保存"""
        output_dir = Path('outputs') / config_data['project_name'] / phase_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = output_dir / 'phase_results.json'
        # 保存用にシリアライズ可能な形式に変換
        serializable_results = {
            theme_id: {
                'report_path': str(data['report_path']),
                'quality': data['quality']
            }
            for theme_id, data in results.items()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
    
    def generate_summary_report(self, config_data):
        """全体サマリーレポートの生成"""
        print("\n📑 全体サマリーレポートを生成中...")
        self.report_generator.generate_summary_report(
            config_data=config_data,
            all_results=self.phase_results
        )

    def run_single_theme(self, config_data, phase_name, theme_id):
        """単一テーマの実行"""
        phase_config = self.load_phase_config(phase_name)
        theme_info = phase_config['themes'].get(theme_id)
        
        if not theme_info:
            print(f"❌ テーマ {theme_id} が見つかりません。")
            return
        
        print(f"\n📝 {theme_id}: {theme_info['name']} を調査中...")
        
        # 3段階の深掘り調査
        theme_results = []
        for step in range(1, 4):
            previous_results = self.get_previous_results(phase_name, theme_id)
            
            result = self.research_engine.execute_research(
                config_data=config_data,
                phase_name=phase_name,
                theme_id=theme_id,
                step=step,
                previous_results=previous_results,
                theme_results=theme_results
            )
            
            theme_results.append(result)
            print(f"  ✓ ステップ {step}/3 完了")
            time.sleep(1)
        
        # レポート生成
        report_path = self.report_generator.generate_theme_report(
            config_data=config_data,
            phase_name=phase_name,
            theme_id=theme_id,
            theme_info=theme_info,
            results=theme_results
        )
        
        # 品質チェック
        quality_result = self.quality_checker.check_report(report_path)
        if quality_result['passed']:
            print(f"  ✅ 品質チェック合格")
        else:
            print(f"  ⚠️  品質チェック要改善: {quality_result['issues']}")
        
        print(f"\n✅ 調査完了: {report_path}") 