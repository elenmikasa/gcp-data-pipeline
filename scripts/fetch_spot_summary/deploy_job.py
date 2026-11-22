"""JEPX スポットサマリー取得ジョブを Cloud Run Jobs にデプロイするスクリプト"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    # scripts/fetch_spot_summary/deploy_job.py -> scripts -> jepx_imbalance
    project_root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(dotenv_path=project_root / ".env")

    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION", "asia-northeast1")
    repository = os.getenv("ARTIFACT_REGISTRY_REPOSITORY")
    gcs_bucket = os.getenv("GCS_BUCKET")

    job_name = "fetch-spot-summary-job"
    image_name = "fetch-spot-summary"
    service_account = os.getenv("CLOUD_RUN_JOB_SERVICE_ACCOUNT")

    if not project_id:
        raise ValueError("環境変数 GCP_PROJECT_ID が設定されていません。")
    if not gcs_bucket:
        raise ValueError("環境変数 GCS_BUCKET が設定されていません。")
    if not repository:
        raise ValueError("環境変数 ARTIFACT_REGISTRY_REPOSITORY が設定されていません。")
    if not service_account:
        raise ValueError("環境変数 CLOUD_RUN_JOB_SERVICE_ACCOUNT が設定されていません。")

    image_uri = f"{region}-docker.pkg.dev/{project_id}/{repository}/{image_name}:latest"
    env_vars = f"GCS_BUCKET={gcs_bucket}"

    cmd = [
        "gcloud",
        "run",
        "jobs",
        "deploy",
        job_name,
        "--image",
        image_uri,
        "--region",
        region,
        "--project",
        project_id,
        "--service-account",
        service_account,
        "--set-env-vars",
        env_vars,
        
    ]

    

    print("--- Cloud Run Job デプロイ開始 ---")
    print(f"Job Name : {job_name}")
    print(f"Image    : {image_uri}")
    print(f"Region   : {region}")
    print(f"Project  : {project_id}")
    print(f"Env Vars : {env_vars}")

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("❌ Cloud Run Job のデプロイに失敗しました。")
        sys.exit(result.returncode)

    print("✨ Cloud Run Job のデプロイが完了しました！")


if __name__ == "__main__":
    main()