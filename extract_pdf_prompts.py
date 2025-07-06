#!/usr/bin/env python
"""
PDFからプロンプトデータを抽出し、prompts_data.jsonを作成するスクリプト
全36テーマ（A, B, 1〜35, Z）の雛形を自動生成
"""
import json
from pathlib import Path

def create_prompts_data_structure():
    """全36テーマのプロンプトデータ雛形を作成"""
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
    
    prompts_data = {}
    for phase, theme_ids in phase_mapping.items():
        prompts_data[phase] = {}
        for theme_id in theme_ids:
            prompts_data[phase][theme_id] = {
                "name": f"TODO: {theme_id}のテーマ名（PDFから転記）",
                "main_question": f"TODO: {theme_id}の主要な問い（PDFから転記）",
                "description": f"TODO: {theme_id}の説明（PDFから転記）",
                "tags": [],
                "variables": [],
                "deliverables": [],
                "steps": {
                    "1": {
                        "role": f"TODO: {theme_id}のステップ1ロール（PDFから転記）",
                        "title": f"TODO: {theme_id}のステップ1タイトル（PDFから転記）"
                    },
                    "2": {
                        "title": f"TODO: {theme_id}のステップ2タイトル（PDFから転記）",
                        "requires_previous": True
                    },
                    "3": {
                        "title": f"TODO: {theme_id}のステップ3タイトル（PDFから転記）",
                        "requires_previous": True
                    }
                }
            }
    return prompts_data

def main():
    print("全36テーマの雛形をprompts_data.jsonに自動生成中...")
    prompts_data = create_prompts_data_structure()
    with open('prompts_data.json', 'w', encoding='utf-8') as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)
    print("✅ 全36テーマの雛形をprompts_data.jsonに保存しました")
    print("📝 各項目はPDFを見ながら埋めてください")

if __name__ == "__main__":
    main() 