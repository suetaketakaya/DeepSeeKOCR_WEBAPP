# Cloud Run用のDockerfile - DeepSeek-OCR Gradio Webアプリ

FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY deepseekuse_gradio.py .
COPY reload_model_cpu.py .
COPY update_model_to_float32.py .

# モデルディレクトリと出力ディレクトリを作成
RUN mkdir -p models output

# 環境変数を設定
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Gradioアプリケーションを起動
# Cloud Runのポート設定に対応
CMD python deepseekuse_gradio.py
