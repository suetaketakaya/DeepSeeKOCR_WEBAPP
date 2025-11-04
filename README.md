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

# 🚀 TrOCR Webapp

Microsoft TrOCRを使用した高精度な光学文字認識（OCR）Webアプリケーション

## ✨ 特徴

| 機能 | 説明 |
|------|------|
| 📖 **高精度OCR** | Microsoft TrOCRによる高精度な文字認識 |
| ⚡ **軽量・高速** | 1.4GBの軽量モデルで高速処理 |
| 💻 **CPU/GPU対応** | 環境に応じて自動的に最適化 |
| 🌐 **Web UI** | Gradioによる使いやすいインターフェース |
| 📱 **レスポンシブ** | モバイルデバイスでも快適に利用可能 |
| 🆓 **完全無料** | 全機能を無料で利用可能 |

## 🎯 使い方

### ステップ1: 画像をアップロード
OCR処理したい画像をドラッグ&ドロップまたはクリックしてアップロード

### ステップ2: テキスト抽出
「テキスト抽出」ボタンをクリックして処理を開始

### ステップ3: 結果を確認
抽出されたテキストが右側に表示されます

## 🔧 技術詳細

このアプリケーションは、Microsoft Researchが開発したTrOCR（Transformer-based OCR）モデルを使用しています。

### 主な技術スタック

- **モデル**: microsoft/trocr-large-printed (1.4GB)
- **フレームワーク**: Hugging Face Transformers
- **UI**: Gradio 4.0+
- **画像処理**: Pillow

### メモリ使用量

- **モデルサイズ**: 約1.4GB
- **推論時メモリ**: 約4-6GB
- **Hugging Face Spaces無料プラン**: ✅ 問題なく動作

## 📊 処理時間の目安

| 画像サイズ | 処理時間（CPU） | 処理時間（GPU） |
|-----------|----------------|----------------|
| 小（<1MB） | 3-5秒 | 1-2秒 |
| 中（1-3MB） | 5-10秒 | 2-3秒 |
| 大（>3MB） | 10-20秒 | 3-5秒 |

※初回起動時はモデルのダウンロードに時間がかかります（2-3分程度）

## 🔗 リンク

- **GitHub リポジトリ**: [DeepSeeKOCR_WEBAPP](https://github.com/suetaketakaya/DeepSeeKOCR_WEBAPP)
- **Firebase ランディングページ**: [deepseekocr-9a570.web.app](https://deepseekocr-9a570.web.app)
- **Hugging Face Space**: [deepseekocr_forwebapp](https://huggingface.co/spaces/Takaya1029/deepseekocr_forwebapp)
- **モデル**: [Microsoft TrOCR](https://huggingface.co/microsoft/trocr-large-printed)

## 📝 ライセンス

Apache 2.0 License

## 👨‍💻 作者

Created by [suetaketakaya](https://github.com/suetaketakaya)

## 🙏 謝辞

- Microsoft ResearchのTrOCRモデル
- Hugging Face Spacesの無料ホスティング
- Gradioフレームワーク
- Firebase Hosting
