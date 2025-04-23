# 基盤となる Python イメージを指定
FROM python:3.9-slim

# 必要なパッケージをインストール
RUN apt-get update \
    && apt-get install -y libpq-dev \
    && apt-get clean

# 作業ディレクトリを設定
WORKDIR /workspace

# requirements.txt をコンテナにコピー
COPY requirements.txt /workspace/

# 必要なパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# コンテナ内で必要なファイルをコピー
COPY . /workspace/

# ポート8000を開放（Djangoのデフォルトポート）
EXPOSE 8000

# Djangoの開発サーバを起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



