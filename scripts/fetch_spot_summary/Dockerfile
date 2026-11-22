FROM python:3.12-slim

# Pythonのログをバッファせず出力し、Cloud Runのログにすぐ反映する。
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fetch_spot_summary.py .

# コンテナ内の実行ユーザーをrootから一般ユーザー（appuser）に切り替え、最小権限で動かす。
RUN useradd --create-home --uid 10001 appuser
USER appuser

CMD ["python", "fetch_spot_summary.py"]