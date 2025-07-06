# Business Strategy Research System 使用ガイド

## クイックスタート

1. **初回セットアップ**
   ```
   Cursorでプロジェクトを開き、「初期設定して」と入力
   ```

2. **設定ファイルの準備**
   - `templates/research_config_template.md` をコピー
   - `project_config.md` として保存
   - 必要事項を記入

3. **調査の実行**
   ```
   python run_research.py
   ```

## Cursor AIでの実行方法

### 方法1: 対話モード（推奨）
1. Cursorで `run_research.py` を開く
2. 「このスクリプトを実行して」と入力
3. 画面の指示に従って選択

### 方法2: 直接指示
- 全体調査: 「全体調査を開始して」
- フェーズ指定: 「フェーズ1の調査を実行して」
- テーマ指定: 「テーマAの調査を実行して」

## トラブルシューティング

### エラー: 設定ファイルが見つかりません
→ `project_config.md` が存在することを確認

### エラー: 必須フィールドが不足
→ 設定ファイルの必須項目をすべて記入

### 調査が途中で停止
→ フェーズ単位で実行してみる

## 高度な使い方

### プロンプトのカスタマイズ
`prompts/` ディレクトリ内のファイルを編集

### 品質基準の調整
`config/system_config.json` の `quality_check` セクションを編集

### 出力形式の変更
将来的にNotion/Google Docs連携を予定 