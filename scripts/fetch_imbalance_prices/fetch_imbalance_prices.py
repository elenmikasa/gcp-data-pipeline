"""指定された年月のインバランス料金CSVを取得し、GCSに保存する。"""

import logging
import os
import re
from email.message import Message
from pathlib import Path

import httpx
from google.cloud import storage

API_URL = "https://www.imbalanceprices-cs.jp/api/1.0/imb/price/{year_month}"


def target_months(value: str | None) -> tuple[str, ...]:
    """TARGET_MONTHS環境変数の値を検証し、年月のタプルとして返す。"""
    if not value:
        raise ValueError("TARGET_MONTHS環境変数を設定してください（例: 202610,202611）。")

    months = tuple(month.strip() for month in value.split(","))
    if any(not re.fullmatch(r"\d{6}", month) for month in months):
        raise ValueError(
            "TARGET_MONTHSはYYYYMM形式の年月をカンマ区切りで指定してください。"
        )
    if any(not 1 <= int(month[4:]) <= 12 for month in months):
        raise ValueError("TARGET_MONTHSの月は01〜12で指定してください。")
    if len(set(months)) != len(months):
        raise ValueError("TARGET_MONTHSに重複した年月があります。")

    return months


def download_csv(client: httpx.Client, year_month: str) -> tuple[bytes, str, str]:
    """指定した月のCSVを取得し、内容、Content-Type、ファイル名を返す。"""
    url = API_URL.format(year_month=year_month)
    response = client.get(url)
    response.raise_for_status()
    logging.info(
        "APIレスポンス: status=%s, Content-Disposition=%r, Content-Type=%r",
        response.status_code,
        response.headers.get("Content-Disposition"),
        response.headers.get("Content-Type"),
    )
    # ファイル名が含まれるContent-Dispositionヘッダーを取得する。
    content_disposition = response.headers.get("Content-Disposition", "")
    # Content-Dispositionを解析するためのオブジェクトを作成する。
    disposition = Message()
    # 取得した値をContent-Dispositionヘッダーとして登録し、ファイル名を解析できるようにする。
    disposition["Content-Disposition"] = content_disposition
    filename = disposition.get_filename()
    if not filename:
        raise RuntimeError(f"{year_month}のレスポンスにファイル名がありません。")
    if Path(filename).name != filename:
        raise RuntimeError(f"レスポンスのファイル名が不正です: {filename!r}")
    # CSV拡張子の直前にあるリビジョン番号（例: _01、_02）を取り除く。
    filename = re.sub(r"_\d+(?=\.csv$)", "", filename, flags=re.IGNORECASE)

    # CSV形式のレスポンスでは、Content-Typeにtext/csvが返る。
    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type or "html" in content_type:
        raise RuntimeError(
            f"{year_month}の取得結果がCSVではありません（Content-Type: "
            f"{content_type!r}）。"
        )
    if not response.content:
        raise RuntimeError(f"{year_month}の取得結果が空です。")

    return response.content, content_type, filename


def upload_csv(
    client: storage.Client,
    bucket_name: str,
    filename: str,
    content: bytes,
    content_type: str,
) -> str:
    """CSVをGCSにアップロードし、gs://形式のURIを返す。"""
    object_name = f"imbalanceprices/{filename}"
    # GCSバケット内の保存先を表すBlobオブジェクトを取得する。
    blob = client.bucket(bucket_name).blob(object_name)
    blob.upload_from_string(content, content_type=content_type)
    return f"gs://{bucket_name}/{object_name}"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    bucket_name = os.getenv("GCS_BUCKET")
    if not bucket_name:
        raise ValueError("GCS_BUCKET環境変数を設定してください。")
    months = target_months(os.getenv("TARGET_MONTHS"))
    logging.info("取得対象年月: %s", ", ".join(months))
    storage_client = storage.Client()

    # 接続確立は10秒、接続後の応答待ちは60秒でタイムアウトする。
    timeout = httpx.Timeout(60.0, connect=10.0)
    with httpx.Client(timeout=timeout) as client:
        for year_month in months:
            content, content_type, filename = download_csv(client, year_month)
            gcs_uri = upload_csv(
                storage_client,
                bucket_name,
                filename,
                content,
                content_type,
            )
            logging.info("%s にアップロードしました（%d bytes）", gcs_uri, len(content))


if __name__ == "__main__":
    main()
