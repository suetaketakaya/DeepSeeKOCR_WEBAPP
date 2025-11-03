# 🤗 Hugging Face Spacesへのデプロイ手順

このドキュメントでは、DeepSeek-OCR GradioアプリをHugging Face Spacesに無料でデプロイする手順を説明します。

---

## 📋 目次

1. [Hugging Face Spacesとは](#hugging-face-spacesとは)
2. [前提条件](#前提条件)
3. [デプロイ手順](#デプロイ手順)
4. [環境変数の設定（AdSense用）](#環境変数の設定adsense用)
5. [カスタムドメインの設定](#カスタムドメインの設定)
6. [トラブルシューティング](#トラブルシューティング)

---

## Hugging Face Spacesとは

**Hugging Face Spaces**は、機械学習モデルやデモアプリを無料でホスティングできるプラットフォームです。

### メリット

| 項目 | 詳細 |
|------|------|
| 💰 **完全無料** | CPU環境は無料、GPU環境も一定時間無料 |
| 🚀 **簡単デプロイ** | GitHubリポジトリと連携して自動デプロイ |
| 📊 **分析機能** | アクセス数や使用状況を確認可能 |
| 🌐 **公開URL** | `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME` で公開 |
| 🔄 **自動更新** | GitHubにpushすると自動的に再デプロイ |

---

## 前提条件

### 必要なアカウント

- ✅ **Hugging Face アカウント**（無料）
  - https://huggingface.co/join でアカウント作成
- ✅ **GitHub アカウント**（オプション、推奨）
  - リポジトリとの連携に使用

---

## デプロイ手順

### 方法1: Webインターフェースから直接アップロード

#### ステップ1: Spaceを作成

1. [Hugging Face](https://huggingface.co/) にログイン
2. 右上のプロフィールアイコンをクリック → **「New Space」** を選択
3. 以下の情報を入力：
   - **Space name**: `deepseek-ocr` （任意の名前）
   - **License**: `MIT` または `Apache 2.0`
   - **Space SDK**: **Gradio** を選択
   - **Space hardware**: **CPU basic** （無料）
   - **Visibility**: Public（公開）または Private（非公開）

4. **「Create Space」** をクリック

#### ステップ2: ファイルをアップロード

作成されたSpaceのページで、以下のファイルをアップロード：

```
deepseek-ocr/
├── deepseekuse_gradio.py  → app.py にリネーム
├── reload_model_cpu.py
├── update_model_to_float32.py
├── requirements.txt
└── README.md
```

**重要**: `deepseekuse_gradio.py` を **`app.py`** にリネームしてアップロードしてください。Hugging Face Spacesは`app.py`を自動的に実行します。

#### ステップ3: requirements.txtを確認

`requirements.txt` に以下が含まれていることを確認：

```txt
torch>=2.0.0
transformers>=4.37.0
accelerate>=0.25.0
sentencepiece>=0.1.99
gradio>=4.0.0
Pillow>=10.0.0
```

#### ステップ4: デプロイ完了を待つ

- アップロード後、自動的にビルドが開始されます
- ビルドログを確認しながら待ちます（初回は10-20分程度）
- ステータスが「Running」になったら完了です

---

### 方法2: GitHubリポジトリから連携（推奨）

#### ステップ1: GitHubリポジトリを準備

既存のリポジトリに以下のファイルを配置：

```bash
cd /Users/suetaketakaya/deepseekocr

# app.pyとしてコピー
cp deepseekuse_gradio.py app.py

# Gitに追加
git add app.py
git commit -m "Add app.py for Hugging Face Spaces"
git push origin main
```

#### ステップ2: Hugging Face Spaceを作成

1. [Hugging Face](https://huggingface.co/) にログイン
2. 「New Space」を選択
3. Space情報を入力（上記と同じ）
4. **「Connect a Git repository」** を選択
5. GitHubリポジトリのURLを入力：
   ```
   https://github.com/suetaketakaya/DeepSeeKOCR_WEBAPP.git
   ```

#### ステップ3: 自動デプロイの設定

- GitHubにpushするたびに、Hugging Face Spacesが自動的に更新されます
- Settings → **「Automatically rebuild on push」** を有効化

---

## 環境変数の設定（AdSense用）

AdSense広告を表示する場合、環境変数を設定します。

### ステップ1: Spaceの設定画面を開く

1. Space のページで **「Settings」** タブをクリック
2. **「Variables and secrets」** セクションに移動

### ステップ2: 環境変数を追加

以下の環境変数を追加：

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `ADSENSE_CLIENT_ID` | `YOUR_CLIENT_ID` | AdSenseクライアントID（数字のみ） |
| `ADSENSE_SLOT_TOP` | `YOUR_SLOT_ID_TOP` | トップバナーのスロットID |
| `ADSENSE_SLOT_BOTTOM` | `YOUR_SLOT_ID_BOTTOM` | ボトムバナーのスロットID |

### ステップ3: Spaceを再起動

環境変数を追加後、Spaceを再起動すると広告が表示されます。

---

## カスタムドメインの設定

Hugging Face Spacesでは、カスタムドメインの設定はサポートされていません。代わりに：

1. **Firebase Hostingでランディングページを公開**
   - カスタムドメイン: `https://your-domain.com`
   - Hugging Face Spacesへのリンクを配置

2. **短縮URLサービスを使用**
   - Bitly、TinyURLなどで短縮URL を作成
   - 例: `https://bit.ly/deepseek-ocr`

---

## トラブルシューティング

### 問題1: ビルドが失敗する

**原因**: 依存関係のエラー

**解決策**: `requirements.txt` を確認

```bash
# ローカルでテスト
pip install -r requirements.txt
python app.py
```

### 問題2: モデルのダウンロードでタイムアウト

**原因**: 初回起動時にモデルをダウンロードするため時間がかかる

**解決策**:
- 初回は20-30分待つ
- ビルドログを確認して進捗を確認

### 問題3: メモリ不足エラー

**原因**: CPU basic（無料プラン）ではメモリが16GBに制限されている

**解決策**:
1. Settings → **「Space hardware」** で **CPU upgrade** を選択（有料）
2. またはモデルを軽量化する

### 問題4: 広告が表示されない

**原因**: 環境変数が設定されていない

**解決策**:
1. Settings → Variables and secretsで環境変数を確認
2. Spaceを再起動

---

## 📊 アクセス分析

Hugging Face Spacesは自動的にアクセス数を記録します：

1. Space のページで **「Analytics」** タブをクリック
2. 訪問者数、実行回数などを確認

---

## 💰 収益化のヒント

### 1. Firebase Hostingと組み合わせる

```
Firebase Hosting (カスタムドメイン + AdSense)
    ↓ (リンク)
Hugging Face Spaces (Gradioアプリ)
```

### 2. SEO対策

Firebase Hostingのランディングページに以下を追加：

```html
<meta name="description" content="高精度OCRツール">
<meta name="keywords" content="OCR, AI, 文字認識">
```

### 3. SNSでの宣伝

- Twitter: ハッシュタグ `#OCR #AI #MachineLearning`
- Reddit: r/MachineLearning, r/learnmachinelearning
- Qiita/Zenn: 技術記事を投稿

---

## 🎉 デプロイ完了チェックリスト

- [ ] Hugging Face アカウントを作成
- [ ] Spaceを作成（SDK: Gradio, Hardware: CPU basic）
- [ ] `app.py` と `requirements.txt` をアップロード
- [ ] ビルドが成功し、Spaceが「Running」状態
- [ ] ブラウザでSpaceにアクセスして動作確認
- [ ] 環境変数を設定（AdSense使用の場合）
- [ ] Firebase HostingのランディングページにSpaceのURLを追加
- [ ] SEO対策とSNSでの宣伝

---

## 🔗 参考リンク

- [Hugging Face Spaces ドキュメント](https://huggingface.co/docs/hub/spaces)
- [Gradio ドキュメント](https://gradio.app/docs/)
- [DeepSeek-OCR モデル](https://huggingface.co/deepseek-ai/DeepSeek-OCR)

---

**作成日**: 2025年
**最終更新**: 2025年
**バージョン**: 1.0
