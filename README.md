---
title: Qwen3-VL OCR Webapp
emoji: 📖
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
---

# 🚀 Qwen3-VL OCR Webapp

Qwen3-VL-2Bを使用した高精度な光学文字認識（OCR）Webアプリケーション

## ✨ 特徴

| 機能 | 説明 |
|------|------|
| 📖 **超高精度OCR** | Qwen3-VL-2Bによる最先端の文字認識 |
| 🌏 **32言語対応** | 日本語・英語・中国語など32言語をサポート |
| 💪 **ロバスト性** | 低照度・ぼかし・傾きがある画像でも高精度 |
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

このアプリケーションは、Alibaba Qwen teamが開発したQwen3-VL（Vision Language Model）を使用しています。

### 主な技術スタック

- **モデル**: Qwen/Qwen3-VL-2B-Instruct (2B params, 約4GB)
- **フレームワーク**: Hugging Face Transformers 4.57.0+
- **UI**: Gradio 4.0+
- **画像処理**: Pillow

### メモリ使用量

- **モデルサイズ**: 約4GB
- **推論時メモリ**: 約6-8GB
- **Hugging Face Spaces無料プラン**: ✅ 問題なく動作

## 📊 処理時間の目安

| 画像サイズ | 処理時間（CPU） | 処理時間（GPU） |
|-----------|----------------|----------------|
| 小（<1MB） | 5-10秒 | 2-4秒 |
| 中（1-3MB） | 10-20秒 | 4-8秒 |
| 大（>3MB） | 20-40秒 | 8-15秒 |

※初回起動時はモデルのダウンロードに時間がかかります（3-5分程度）

## 🌟 Qwen3-VLの優位性

### TrOCRからのアップグレード

| 項目 | TrOCR | Qwen3-VL-2B |
|------|-------|-------------|
| 対応言語 | 英語中心 | **32言語** |
| 日本語精度 | 低い | **高い** |
| 低照度対応 | ❌ | ✅ |
| 傾き補正 | ❌ | ✅ |
| 専門用語 | 弱い | **強い** |
| リリース | 2021 | **2025年9月** |

### 対応言語（一部）

日本語、英語、中国語（簡体字・繁体字）、韓国語、フランス語、ドイツ語、スペイン語、イタリア語、ポルトガル語、ロシア語、アラビア語、ヒンディー語など

## 🔗 リンク

- **GitHub リポジトリ**: [DeepSeeKOCR_WEBAPP](https://github.com/suetaketakaya/DeepSeeKOCR_WEBAPP)
- **Firebase ランディングページ**: [deepseekocr-9a570.web.app](https://deepseekocr-9a570.web.app)
- **Hugging Face Space**: [deepseekocr_forwebapp](https://huggingface.co/spaces/Takaya1029/deepseekocr_forwebapp)
- **モデル**: [Qwen3-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct)

## 📝 ライセンス

Apache 2.0 License

## 👨‍💻 作者

Created by [suetaketakaya](https://github.com/suetaketakaya)

## 🙏 謝辞

- Alibaba Qwen teamのQwen3-VLモデル
- Hugging Face Spacesの無料ホスティング
- Gradioフレームワーク
- Firebase Hosting
