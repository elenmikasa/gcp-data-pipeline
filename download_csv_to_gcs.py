import os

from dotenv import load_dotenv
import requests
from google.cloud import storage


load_dotenv()

url = "https://www.jepx.jp/_download.php"
payload = {
    "dir": "spot_summary",
    "file": "spot_summary_2026.csv",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "Referer": "https://www.jepx.jp/electricpower/market-data/spot/",
    "Origin": "https://www.jepx.jp",
    "Content-Type": "application/x-www-form-urlencoded",
}


def main() -> None:
    bucket_name = os.environ.get("GCS_BUCKET")
    if not bucket_name:
        raise SystemExit("環境変数 GCS_BUCKET に保存先のGCSバケット名を設定してください。")

    print("データをダウンロード中...")
    response = requests.post(url, data=payload, headers=headers, timeout=30)
    response.raise_for_status()
    if not response.content:
        raise RuntimeError("ダウンロードしたファイルが空です。")

    content_type = response.headers.get("Content-Type")
    if content_type:
        print(f"レスポンスのContent-Type: {content_type}")
    else:
        print("レスポンスにContent-Typeがありません。汎用のバイナリ形式を使用します。")

    client = storage.Client()
    # GCSバケット内の保存先オブジェクトを、アップロードするファイル名で指定する。
    blob = client.bucket(bucket_name).blob(payload["file"])
    blob.upload_from_string(
        response.content,
        content_type="text/csv",
    )

    print(f"成功: gs://{bucket_name}/{blob.name} に保存しました。")


if __name__ == "__main__":
    main()
