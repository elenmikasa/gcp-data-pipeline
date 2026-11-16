"""元CSVから必要列を抽出し、整形済みCSVをGCSに保存する。"""

import csv
import io
import logging
import os

from google.cloud import storage

SOURCE_PREFIX = "imbalanceprices/"
HISTORY_PREFIX = "imbalanceprices/processed/history/"
LATEST_PREFIX = "imbalanceprices/processed/latest/"

OUTPUT_COLUMNS = (
    "target_date",
    "time_slot",
    "time_start",
    "time_end",
    "hokkaido",
    "tohoku",
    "tokyo",
    "chubu",
    "hokuriku",
    "kansai",
    "chugoku",
    "shikoku",
    "kyushu",
)


def format_csv(raw_content: bytes, source_name: str) -> bytes:
    """MS932の元CSVから必要な列を抽出し、UTF-8 CSVに整形する。"""
    # MS932のバイトデータをPythonで扱える文字列に変換する。
    text = raw_content.decode("ms932")
    # io.StringIOで文字列をファイルのように扱い、newline=""で改行を自動変換せずCSVリーダーに渡す。
    source_reader = csv.reader(io.StringIO(text, newline=""))
    # 整形後のCSVを書き込むためのメモリ上のファイルを用意する。
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(OUTPUT_COLUMNS)

    data_count = 0
    for row in source_reader:
        if not row or row[0] != "D":
            continue

        # 余剰インバランス料金単価を抽出する。rangeは列番号5から22未満まで2つずつ進む。
        surplus_prices = [row[index] for index in range(5, 22, 2)]
        # *で各リストを展開し、4項目と9エリアの料金を1行として書き込む。
        writer.writerow([*row[1:5], *surplus_prices])
        data_count += 1

    if data_count == 0:
        raise ValueError(f"{source_name} にデータ行がありません。")

    # outputはStringIOオブジェクトなので、getvalue()で中身の文字列を取り出してUTF-8のバイト列にする。
    return output.getvalue().encode("utf-8")


def list_target_source_files(
    bucket: storage.Bucket, target_months: tuple[str, ...]
) -> dict[str, tuple[storage.Blob, str]]:
    """バケット直下から、対象月の条件に一致するCSVファイルを列挙する。"""
    files: dict[str, tuple[storage.Blob, str]] = {}
    
    # imbalanceprices/で始まるGCSオブジェクトを列挙する
    for blob in bucket.list_blobs(prefix=SOURCE_PREFIX):
        filename = blob.name.removeprefix(SOURCE_PREFIX)
        if "/" in filename or not filename.endswith(".csv"):
            continue

        # ファイル名の先頭6文字を年月として取得する（例: "202611_imbalance-price_01.csv" -> "202611"）[cite: 1]
        year_month = filename[:6]
        
        # ワークフローから指定された対象月に含まれる場合のみ採用する
        if year_month in target_months:
            files[year_month] = (blob, filename)

    if not files:
        raise FileNotFoundError(
            f"gs://{bucket.name}/{SOURCE_PREFIX} に対象月 ({target_months}) のCSVがありません。"
        )
    return files


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    bucket_name = os.getenv("GCS_BUCKET")
    if not bucket_name:
        raise ValueError("環境変数 GCS_BUCKET が設定されていません。")

    target_months_env = os.getenv("TARGET_MONTHS")
    if not target_months_env:
        raise ValueError("環境変数 TARGET_MONTHS が設定されていません。")

    # カンマ区切りの文字列をタプルに変換する（例: "202610,202611" -> ("202610", "202611")）
    target_months_tuple = tuple(m.strip() for m in target_months_env.split(","))

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # 最初から対象月に絞ったファイル一覧を取得する
    source_files = list_target_source_files(bucket, target_months_tuple)

    formatted_files: dict[str, tuple[str, bytes]] = {}
    for year_month, (blob, filename) in sorted(source_files.items()):
        # download_as_bytes()でGCS上の元CSVをバイトデータとして取得する。
        formatted_files[year_month] = (
            filename,
            format_csv(blob.download_as_bytes(), blob.name),
        )

    # 取得できたファイル群はすべて「処理すべき最新対象月」となるため、latestフォルダの既存分をクリアして更新
    for blob in bucket.list_blobs(prefix=LATEST_PREFIX):
        if blob.name.endswith(".csv"):
            blob.delete()
            logging.info(
                "既存のlatest CSVを削除しました: gs://%s/%s",
                bucket_name,
                blob.name,
            )

    for year_month, (filename, content) in formatted_files.items():
        object_name = f"{LATEST_PREFIX}{filename}"
        bucket.blob(object_name).upload_from_string(
            content,
            content_type="text/csv; charset=utf-8",
        )
        logging.info("latestに保存しました: gs://%s/%s", bucket_name, object_name)

    for year_month, (filename, content) in formatted_files.items():
        object_name = f"{HISTORY_PREFIX}{filename}"
        bucket.blob(object_name).upload_from_string(
            content,
            content_type="text/csv; charset=utf-8",
        )
        logging.info("historyに保存しました: gs://%s/%s", bucket_name, object_name)


if __name__ == "__main__":
    main()