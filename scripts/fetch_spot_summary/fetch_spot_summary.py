from datetime import datetime
import os

from google.cloud import storage
import requests

URL = "https://www.jepx.jp/_download.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "Referer": "https://www.jepx.jp/electricpower/market-data/spot/",
    "Origin": "https://www.jepx.jp",
    "Content-Type": "application/x-www-form-urlencoded",
}


def get_fiscal_year(today: datetime | None = None) -> int:
    """現在の日付から年度（4月始まり）を返す。"""
    if today is None:
        today = datetime.now()
    return today.year if today.month >= 4 else today.year - 1


def main() -> None:
    bucket_name = os.environ.get("GCS_BUCKET")
    if not bucket_name:
        raise SystemExit("環境変数 GCS_BUCKET に保存先のGCSバケット名を設定してください。")

    fiscal_year = get_fiscal_year()
    filename = f"spot_summary_{fiscal_year}.csv"
    payload = {
        "dir": "spot_summary",
        "file": filename,
    }

    print(f"対象年度: {fiscal_year}年度 / ファイル名: {filename}")
    print("データをダウンロード中...")
    response = requests.post(URL, data=payload, headers=HEADERS, timeout=30)
    response.raise_for_status()
    if not response.content:
        raise RuntimeError("ダウンロードしたファイルが空です。")

    content_type = response.headers.get("Content-Type")
    if content_type:
        print(f"レスポンスのContent-Type: {content_type}")
    else:
        print("レスポンスにContent-Typeがありません。汎用のバイナリ形式を使用します。")

    client = storage.Client()
    blob = client.bucket(bucket_name).blob(filename)
    blob.upload_from_string(
        response.content,
        content_type="text/csv",
    )

    print(f"成功: gs://{bucket_name}/{blob.name} に保存しました。")


if __name__ == "__main__":
    main()