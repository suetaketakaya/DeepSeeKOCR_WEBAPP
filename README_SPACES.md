---
title: DeepSeek-OCR Webapp
emoji: 📖
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
---

# 🚀 DeepSeek-OCR Webapp

高精度な光学文字認識（OCR）とMarkdown変換を提供する無料Webアプリケーション

## ✨ 特徴

| 機能 | 説明 |
|------|------|
| 📖 **高精度OCR** | DeepSeek-OCRモデルによる高精度な文字認識 |
| 📄 **Markdown変換** | 文書を構造化されたMarkdownに自動変換 |
| 📦 **バウンディングボックス** | 検出された文字領域を視覚的に表示 |
| 🧮 **数式・表の認識** | 複雑な数式や表の構造も正確に認識 |
| 💻 **CPU対応** | GPUなしでも動作する最適化実装 |
| 🆓 **完全無料** | 全機能を無料で利用可能 |

## 🎯 使い方

### ステップ1: 画像をアップロード
OCR処理したい画像をドラッグ&ドロップまたはクリックしてアップロード

### ステップ2: 処理タイプを選択
- **OCR**: 画像からテキストを抽出
- **Markdown**: 文書をMarkdown形式に変換

### ステップ3: クロップモードを設定
画像の前処理を有効化して認識精度を向上（オプション）

### ステップ4: 処理実行
「処理実行」ボタンをクリックして処理を開始

### ステップ5: 結果を確認
- テキスト結果が左側に表示されます
- バウンディングボックス付き画像が右側に表示されます

## 🔧 技術詳細

このアプリケーションは、DeepSeek社が提供する高性能なVision-Languageモデルをベースにしています。

### CPU環境での動作

GPU環境を前提としたモデルをCPU環境で動作させるため、以下の技術を実装：

- **型変換**: BFloat16 → Float32への自動変換
- **モンキーパッチ**: torch.cuda()などのGPU呼び出しをCPU互換に変換
- **Embedding層の保護**: 整数型テンソルを保護しながら浮動小数点型のみ変換

## 📊 処理時間の目安

| 画像サイズ | 処理時間（CPU） |
|-----------|----------------|
| 小（<1MB） | 30秒〜1分 |
| 中（1-3MB） | 1〜2分 |
| 大（>3MB） | 2〜5分 |

※初回起動時はモデルのダウンロードに時間がかかります（5-10分程度）

## 🔗 リンク

- **GitHub リポジトリ**: [DeepSeeKOCR_WEBAPP](https://github.com/suetaketakaya/DeepSeeKOCR_WEBAPP)
- **Firebase ランディングページ**: [deepseekocr-9a570.web.app](https://deepseekocr-9a570.web.app)
- **元モデル**: [DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR)

## 📝 ライセンス

Apache 2.0 License

## 👨‍💻 作者

Created by [suetaketakaya](https://github.com/suetaketakaya)

## 🙏 謝辞

- DeepSeek社のDeepSeek-OCRモデル
- Hugging Face Spacesの無料ホスティング
- Gradioフレームワーク
