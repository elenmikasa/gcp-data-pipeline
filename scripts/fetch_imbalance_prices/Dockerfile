FROM python:3.12-slim

# Pythonのログをバッファせず出力し、Cloud Runのログにすぐ反映する。
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fetch_imbalance_prices.py .

RUN useradd --create-home --uid 10001 appuser
USER appuser

CMD ["python", "fetch_imbalance_prices.py"]