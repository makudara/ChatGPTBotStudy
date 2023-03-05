# 基本となるDockerイメージを選択
FROM python:3.9-slim-buster

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ワーキングディレクトリを設定
WORKDIR /app

# 必要なPythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# OpenAI APIキーを環境変数に設定
ENV OPENAI_API_KEY=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

# Discordのbotを起動するコマンドを定義
CMD ["python", "bot.py"]

# ホストマシンのファイルをコンテナにコピー
COPY . .

# ポート番号を公開
EXPOSE 8000