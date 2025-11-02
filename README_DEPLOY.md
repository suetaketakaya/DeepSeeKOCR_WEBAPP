# 🚀 DeepSeek-OCR Webapp デプロイ手順書

このドキュメントでは、DeepSeek-OCR GradioアプリケーションをFirebase Hosting + Google Cloud Run環境にデプロイし、Google AdSenseで広告収入を得る体系を整える手順を説明します。

---

## 📋 目次

1. [前提条件](#前提条件)
2. [Google Cloud / Firebase プロジェクトのセットアップ](#google-cloud--firebase-プロジェクトのセットアップ)
3. [Google AdSense の設定](#google-adsense-の設定)
4. [Cloud Run へのデプロイ](#cloud-run-へのデプロイ)
5. [Firebase Hosting の設定](#firebase-hosting-の設定)
6. [カスタムドメインの設定（オプション）](#カスタムドメインの設定オプション)
7. [運用とメンテナンス](#運用とメンテナンス)
8. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必要なアカウント

- ✅ **Google Cloud アカウント**（クレジットカード登録が必要）
- ✅ **Firebase プロジェクト**
- ✅ **Google AdSense アカウント**（広告収入用）

### 必要なツール

```bash
# Google Cloud SDK のインストール
# macOS
brew install --cask google-cloud-sdk

# その他のOSの場合は公式サイトからダウンロード:
# https://cloud.google.com/sdk/docs/install

# Firebase CLI のインストール
npm install -g firebase-tools

# Docker のインストール（ローカルテスト用）
# https://www.docker.com/get-started
```

### ローカル環境の確認

```bash
# Google Cloud SDK のバージョン確認
gcloud --version

# Firebase CLI のバージョン確認
firebase --version

# Docker のバージョン確認
docker --version
```

---

## Google Cloud / Firebase プロジェクトのセットアップ

### 1. Google Cloud プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 「プロジェクトを作成」をクリック
3. プロジェクト名を入力（例: `deepseek-ocr-webapp`）
4. プロジェクトIDをメモ（後で使用）

### 2. 必要なAPIの有効化

```bash
# プロジェクトIDを環境変数に設定
export PROJECT_ID="YOUR_PROJECT_ID"

# Google Cloud プロジェクトを設定
gcloud config set project $PROJECT_ID

# 必要なAPIを有効化
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  firebasehosting.googleapis.com
```

### 3. Firebase プロジェクトの初期化

```bash
# Firebase にログイン
firebase login

# Firebase プロジェクトを初期化
firebase init hosting

# 質問に対する回答:
# - "What do you want to use as your public directory?" → public
# - "Configure as a single-page app?" → No
# - "Set up automatic builds and deploys with GitHub?" → No
```

### 4. .firebaserc ファイルの更新

`.firebaserc` ファイルを開いて、プロジェクトIDを実際の値に置き換えます:

```json
{
  "projects": {
    "default": "YOUR_PROJECT_ID"
  }
}
```

---

## Google AdSense の設定

### 1. AdSense アカウントの作成

1. [Google AdSense](https://www.google.com/adsense/) にアクセス
2. 「利用を開始」をクリック
3. サイト情報を入力して申請
4. 審査に合格するまで待つ（通常1〜2週間）

### 2. 広告ユニットの作成

1. AdSense ダッシュボードにログイン
2. 「広告」→「広告ユニットごと」→「ディスプレイ広告」を選択
3. 広告ユニットを作成:
   - **トップバナー広告**: レスポンシブ
   - **ボトムバナー広告**: レスポンシブ

### 3. AdSense コードの取得

1. 広告ユニットのコードをコピー
2. 以下の値をメモ:
   - **クライアントID**: `ca-pub-XXXXXXXXXXXXXXXXX`
   - **広告スロットID (トップ)**: `XXXXXXXXXX`
   - **広告スロットID (ボトム)**: `XXXXXXXXXX`

### 4. 環境変数の設定

後ほどCloud Runデプロイ時に使用するため、以下の値を環境変数として準備:

```bash
export ADSENSE_CLIENT_ID="XXXXXXXXXXXXXXXXX"  # ca-pub- の後の数字のみ
export ADSENSE_SLOT_TOP="XXXXXXXXXX"
export ADSENSE_SLOT_BOTTOM="XXXXXXXXXX"
```

---

## Cloud Run へのデプロイ

### 方法1: Cloud Build を使った自動デプロイ（推奨）

```bash
# プロジェクトディレクトリに移動
cd /path/to/deepseekocr

# Cloud Build を使ってビルド & デプロイ
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_ADSENSE_CLIENT_ID="$ADSENSE_CLIENT_ID",_ADSENSE_SLOT_TOP="$ADSENSE_SLOT_TOP",_ADSENSE_SLOT_BOTTOM="$ADSENSE_SLOT_BOTTOM"
```

### 方法2: 手動デプロイ

```bash
# Dockerイメージをビルド
docker build -t gcr.io/$PROJECT_ID/deepseek-ocr-webapp:latest .

# Container Registryにプッシュ
docker push gcr.io/$PROJECT_ID/deepseek-ocr-webapp:latest

# Cloud Runにデプロイ
gcloud run deploy deepseek-ocr-webapp \
  --image gcr.io/$PROJECT_ID/deepseek-ocr-webapp:latest \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --set-env-vars "PORT=8080,ADSENSE_CLIENT_ID=$ADSENSE_CLIENT_ID,ADSENSE_SLOT_TOP=$ADSENSE_SLOT_TOP,ADSENSE_SLOT_BOTTOM=$ADSENSE_SLOT_BOTTOM"
```

### デプロイ後の確認

```bash
# Cloud Run サービスのURLを取得
gcloud run services describe deepseek-ocr-webapp \
  --region asia-northeast1 \
  --format="value(status.url)"
```

ブラウザでURLにアクセスして、アプリケーションが正常に動作することを確認します。

---

## Firebase Hosting の設定

Firebase Hostingを使うことで、カスタムドメインやCDN、SSL証明書の自動管理などのメリットがあります。

### 1. firebase.json の確認

`firebase.json` ファイルを開いて、Cloud Runサービスの設定を確認:

```json
{
  "hosting": {
    "public": "public",
    "rewrites": [
      {
        "source": "**",
        "run": {
          "serviceId": "deepseek-ocr-webapp",
          "region": "asia-northeast1"
        }
      }
    ]
  }
}
```

### 2. Firebase Hosting へデプロイ

```bash
# Firebase Hostingにデプロイ
firebase deploy --only hosting
```

### 3. デプロイ後のURLを確認

```bash
# Firebase HostingのURLを表示
firebase hosting:channel:list
```

デフォルトでは `https://YOUR_PROJECT_ID.web.app` または `https://YOUR_PROJECT_ID.firebaseapp.com` でアクセスできます。

---

## カスタムドメインの設定（オプション）

独自ドメインを使用する場合:

### 1. Firebase コンソールでドメイン追加

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. プロジェクトを選択
3. 「Hosting」→「ドメインを追加」をクリック
4. 所有するドメインを入力（例: `deepseek-ocr.example.com`）
5. DNSレコードの設定指示に従う

### 2. DNS レコードの設定

ドメインレジストラ（お名前.com、CloudFlareなど）で以下のレコードを追加:

```
タイプ: A
名前: @（またはドメイン名）
値: Firebase Hostingが提供するIPアドレス
```

### 3. SSL証明書の自動発行

Firebase Hostingは自動的にLet's EncryptのSSL証明書を発行します（数時間かかる場合があります）。

---

## 運用とメンテナンス

### コスト管理

#### Cloud Run の料金

- **無料枠**: 月200万リクエストまで無料
- **料金計算**: [Cloud Run 料金計算ツール](https://cloud.google.com/run/pricing)

#### Firebase Hosting の料金

- **無料枠**: 月10GBの転送まで無料
- **料金**: [Firebase Hosting 料金](https://firebase.google.com/pricing)

### モニタリング

```bash
# Cloud Runのログを確認
gcloud run services logs read deepseek-ocr-webapp \
  --region asia-northeast1 \
  --limit 100

# Firebase Hostingのトラフィック確認
firebase hosting:channel:open
```

### スケーリング設定の調整

リクエスト数が増えた場合、最大インスタンス数を増やします:

```bash
gcloud run services update deepseek-ocr-webapp \
  --region asia-northeast1 \
  --max-instances 50
```

### 広告収入の確認

1. [Google AdSense](https://www.google.com/adsense/) にログイン
2. 「レポート」で収益を確認

---

## トラブルシューティング

### 問題1: Cloud Runデプロイが失敗する

**原因**: メモリ不足

**解決策**: メモリを増やす

```bash
gcloud run services update deepseek-ocr-webapp \
  --region asia-northeast1 \
  --memory 8Gi
```

### 問題2: 広告が表示されない

**原因**: AdSense環境変数が設定されていない

**解決策**: 環境変数を確認して再デプロイ

```bash
# 現在の環境変数を確認
gcloud run services describe deepseek-ocr-webapp \
  --region asia-northeast1 \
  --format="value(spec.template.spec.containers[0].env)"

# 環境変数を再設定
gcloud run services update deepseek-ocr-webapp \
  --region asia-northeast1 \
  --set-env-vars "ADSENSE_CLIENT_ID=$ADSENSE_CLIENT_ID,ADSENSE_SLOT_TOP=$ADSENSE_SLOT_TOP,ADSENSE_SLOT_BOTTOM=$ADSENSE_SLOT_BOTTOM"
```

### 問題3: タイムアウトエラー

**原因**: モデルの読み込みに時間がかかる

**解決策**: タイムアウトを延長

```bash
gcloud run services update deepseek-ocr-webapp \
  --region asia-northeast1 \
  --timeout 900  # 15分
```

### 問題4: Firebase Hostingのリダイレクトが動作しない

**原因**: Cloud Run サービスの権限不足

**解決策**: IAM権限を設定

```bash
gcloud run services add-iam-policy-binding deepseek-ocr-webapp \
  --region=asia-northeast1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

---

## 📞 サポート

問題が解決しない場合:

- **GitHub Issues**: https://github.com/suetaketakaya/DeepSeeKOCR_WEBAPP/issues
- **Google Cloud サポート**: https://cloud.google.com/support
- **Firebase サポート**: https://firebase.google.com/support

---

## 🎉 デプロイ完了チェックリスト

- [ ] Google Cloud プロジェクトを作成
- [ ] 必要なAPIを有効化
- [ ] Firebase プロジェクトを初期化
- [ ] Google AdSense アカウントを作成して承認を得る
- [ ] 広告ユニットを作成してIDを取得
- [ ] Cloud Run にデプロイ
- [ ] Firebase Hosting にデプロイ
- [ ] カスタムドメインを設定（オプション）
- [ ] 広告が正しく表示されることを確認
- [ ] モニタリングとログの確認体制を整える

全てのチェックが完了したら、あなたのDeepSeek-OCR Webアプリは広告収入を得られる状態で公開されています！

---

## 💰 収益化のヒント

1. **SEO対策**: Webページにメタタグを追加して検索エンジンに最適化
2. **SNSでの宣伝**: Twitter、Facebook、Redditなどでアプリを紹介
3. **ブログ記事**: Qiita、Zenn、Mediumなどで使い方を記事にする
4. **機能追加**: ユーザーのフィードバックを受けて機能を追加
5. **パフォーマンス最適化**: ページ読み込み速度を改善してユーザー体験を向上

---

**作成日**: 2025年
**最終更新**: 2025年
**バージョン**: 1.0
