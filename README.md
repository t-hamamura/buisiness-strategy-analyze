# Business Strategy Research System (BSRS)

ビジネス戦略研究のための自動化システムです。指定されたトピックについて包括的なリサーチを行い、構造化されたレポートを生成します。

## 🚀 機能

- **自動Web検索**: 指定トピックに関する最新情報を自動収集
- **構造化レポート生成**: マークダウン形式で整理されたレポートを出力
- **品質管理**: 自動品質チェック機能付き
- **設定可能**: JSON設定ファイルでカスタマイズ可能

## 📁 プロジェクト構成

```
buisiness-strategy-analyze/
├── src/                    # メインソースコード
│   ├── main.py            # メインコントローラー
│   ├── controller/        # コントローラー層
│   ├── engine/           # リサーチエンジン
│   ├── generator/        # レポート生成
│   └── utils/            # ユーティリティ
├── config/               # 設定ファイル
├── prompts/              # プロンプトテンプレート
├── templates/            # レポートテンプレート
├── outputs/              # 出力ディレクトリ
├── tests/                # テストファイル
├── run_research.py       # 実行スクリプト
├── setup.py             # セットアップスクリプト
├── requirements.txt     # 依存パッケージ
└── USAGE.md             # 詳細使用方法
```

## 🛠️ セットアップ

### 1. 環境準備

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. 初期セットアップ

```bash
python setup.py
```

## 📖 使用方法

### 基本的な使用方法

```bash
python run_research.py "研究したいトピック"
```

### 詳細な使用方法

詳細な使用方法については [USAGE.md](USAGE.md) を参照してください。

## 🔧 設定

`config/phase_config.json` で以下の設定が可能です：

- リサーチフェーズの設定
- 出力フォーマットのカスタマイズ
- 品質基準の調整

## 📝 出力例

システムは以下の形式でレポートを生成します：

```markdown
# トピック名

## 概要
研究結果の概要

## 主要な発見
- 発見1
- 発見2

## 詳細分析
詳細な分析結果

## 結論
研究の結論
```

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。 