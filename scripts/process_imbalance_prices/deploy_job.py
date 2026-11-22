""" .env から設定を読み込み、Cloud Run Jobs をデプロイするスクリプト """

import os
import platform
from pathlib import Path
from dotenv import load_dotenv
import subprocess

def main() -> None:
    # 1. プロジェクトルートの .env を読み込む
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # 2. 必要な環境変数や設定値をまとめて取得・定義する
    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION", "asia-northeast1")
    repository = os.getenv("ARTIFACT_REGISTRY_REPOSITORY")
    gcs_bucket = os.getenv("GCS_BUCKET")
    target_months = "202610"

    # 必須チェック
    if not project_id or not repository:
        raise ValueError("環境変数 (GCP_PROJECT_ID または ARTIFACT_REGISTRY_REPOSITORY) が設定されていません。")
    if not gcs_bucket:
        raise ValueError("環境変数 GCS_BUCKET が設定されていません。")

    # ジョブ名やコンテナイメージの名称を定義
    job_name = "process-imbalance-prices-job"
    image_name = "process-imbalance-prices"  # Artifact Registry上で管理するコンテナイメージ名

    registry_host = f"{region}-docker.pkg.dev"
    image_tag = f"{registry_host}/{project_id}/{repository}/{image_name}:latest"

    # Cloud Run Jobs に渡す環境変数をカンマ区切りでまとめる
    env_vars_to_set = (
        f"GCS_BUCKET={gcs_bucket},"
        f"TARGET_MONTHS={target_months}"
    )

    print(f"--- Cloud Run Job デプロイ開始: {job_name} ---")

    # 3. gcloud run jobs deploy コマンドの組み立て
    cmd = [
        "gcloud",
        "run",
        "jobs",
        "deploy",
        job_name,
        "--image",
        image_tag,
        "--region",
        region,
        "--set-env-vars",
        env_vars_to_set,
        # --quiet: 確認プロンプトや冗長な出力を抑制し、自動実行で処理が止まらないようにする
        "--quiet",
    ]

    # Windows環境考慮の shell 切り替え
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        cmd_str = " ".join(cmd)
        result = subprocess.run(cmd_str, shell=True)
    else:
        result = subprocess.run(cmd, shell=False)

    if result.returncode != 0:
        print("❌ Cloud Run Job のデプロイに失敗しました。")
        exit(result.returncode)
    else:
        print(f"✨ Cloud Run Job '{job_name}' のデプロイが完了しました！")
        print(f"👉 実行コマンド例: gcloud run jobs execute {job_name} --region {region}")

if __name__ == "__main__":
    main()