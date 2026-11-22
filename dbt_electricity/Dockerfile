FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir dbt-bigquery

# 1つ目の「.」: コピー元（ビルド実行時の基準ディレクトリ、ここでは dbt_electricity 配下）
# 2つ目の「.」: コピー先（コンテナ内の作業ディレクトリ、ここでは WORKDIR で指定した /app）
# ※不要なファイル（logs や target など）も含まれやすいため、除外したい場合は .dockerignore を配置する
COPY . .

# dbt パッケージをインストール
RUN dbt deps --profiles-dir .

CMD ["dbt", "build", "--profiles-dir", "."]