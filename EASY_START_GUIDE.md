# EASY START GUIDE

## Business Strategy Research System (BSRS) - かんたんスタートガイド

---

### 1. 必要な環境
- Python 3.9 以上
- pip（Pythonパッケージ管理ツール）
- インターネット接続

---

### 2. セットアップ手順

1. **リポジトリをクローン**
    ```bash
    git clone https://github.com/t-hamamura/buisiness-strategy-analyze.git
    cd buisiness-strategy-analyze
    ```

2. **仮想環境の作成（推奨）**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
    ```

3. **依存パッケージのインストール**
    ```bash
    pip install -r requirements.txt
    ```

4. **初回セットアップ**
    - 以下のコマンドで初期設定・プロンプト生成を自動実行します。
    ```bash
    python run_research.py
    ```
    - 必要な設定ファイルやプロンプトが自動生成されます。

---

### 3. 使い方（基本フロー）

1. **テーマ・フェーズを選択し、調査を実行**
    - `python run_research.py` を実行すると、対話形式でテーマやモードを選択できます。
    - 指示に従い、Cursorのチャット欄でプロンプトを実行し、結果を貼り付けて進めます。

2. **レポート・図表の自動生成**
    - 調査結果に基づき、レポートや図表（SWOT分析、競合マップ等）が自動生成されます。
    - 生成物は `outputs/` ディレクトリに保存されます。

---

### 4. よくある質問

- **Q. 途中でエラーが出た場合は？**
    - `requirements.txt` のパッケージを再インストールしてください。
    - Pythonのバージョンや依存関係に注意してください。

- **Q. 図表が文字化けする場合は？**
    - 日本語フォントがインストールされているかご確認ください。
    - `Meiryo` や `Yu Gothic` などのフォントが推奨です。

- **Q. どのディレクトリで作業すればいい？**
    - 必ず `buisiness-strategy-analyze` ディレクトリ内で作業してください。

---

### 5. サポート
- 詳細な使い方やカスタマイズ方法は `USAGE.md` を参照してください。
- 不明点はGitHub Issuesでご質問ください。 