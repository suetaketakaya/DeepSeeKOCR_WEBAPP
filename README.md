# DeepSeek-OCR ローカル実行

## 概要
DeepSeek-OCRモデルをローカルに保存し、次回以降はインターネット接続なしで実行できるようにします。
画像OCR処理とMarkdown変換のチャットツールが利用可能です。

## セットアップ

### 1. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

### 2. モデルのダウンロード（初回のみ）

CPU環境の場合は、まずモデルをfloat32で保存する必要があります：

```bash
# CPU環境用にモデルを再ダウンロード（推奨）
python reload_model_cpu.py
```

または、既存のモデルを更新：

```bash
# 既存のモデルをfloat32に更新
python update_model_to_float32.py
```

モデルは `./models/deepseek-ocr/` に保存されます。

### 3. チャットツールの使用方法

#### 方法1: コマンドライン版（deepseekuse.py）
```bash
python deepseekuse.py
```

対話形式で画像パスを入力してOCR処理を実行します。

**画像パスの入力例:**
- `test.png` （相対パス）
- `./test.png`
- `/Users/suetaketakaya/deepseekocr/test.png` （絶対パス）
- クォート（' や "）で囲んでも自動的に処理されます

#### 方法2: Web UI版（Gradio）
```bash
python deepseekuse_gradio.py
```

ブラウザで `http://localhost:7860` にアクセスして、GUIで画像を処理できます。

## 機能

### 処理タイプ
- **OCR**: 画像からテキストを抽出
- **Markdown**: ドキュメントをMarkdown形式に変換

### 設定オプション
- **クロップモード**: 画像をクロップして処理（精度向上）
- **保存先**: 結果は `./output` ディレクトリに保存されます

## 保存先
- モデル: `./models/deepseek-ocr/`
- 結果: `./output/`

## トラブルシューティング

### CPU環境でのエラー
CPU環境で `bfloat16` エラーが発生する場合：

```bash
# モデルをfloat32に再変換
python update_model_to_float32.py
```

または、モデルを再ダウンロード：

```bash
# CPU環境用にモデルを再ダウンロード
python reload_model_cpu.py
```

## 注意事項
- モデルファイルは約12GBになります
- モデルは一度ダウンロードすれば、その後はオフラインで使用できます
- `.gitignore` により、モデルファイルはGit管理外に設定されています
- **CPUモード対応**: GPUがない環境でもCPUで動作します（v0.2より）
- **推奨**: GPUがある場合は高速な処理が可能です
