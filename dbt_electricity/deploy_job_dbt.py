""" dbt-electricity 用の Cloud Run Jobs をデプロイするスクリプト（単体完結版） """

import os
import platform
import subprocess
from pathlib import Path
from dotenv import load_dotenv


def main() -> None:
    # 1. プロジェクトルートの .env を読み込む
    # dbt_electricity/deploy_job_dbt.py から見て 2 つ上がプロジェクトルート（.env がある場所）
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # 2. 必要な環境変数や設定値をまとめて取得・定義する
    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION", "asia-northeast1")
    repository = os.getenv("ARTIFACT_REGISTRY_REPOSITORY")
    service_account = os.getenv("DBT_JOB_SERVICE_ACCOUNT")

    # 必須チェック
    if not project_id or not repository:
        raise ValueError(
            "環境変数 (GCP_PROJECT_ID または ARTIFACT_REGISTRY_REPOSITORY) が設定されていません。"
        )
    if not service_account:
        raise ValueError("環境変数 DBT_JOB_SERVICE_ACCOUNT が設定されていません。")

    # ジョブ名やコンテナイメージの名称を定義
    job_name = "dbt-electricity-job"
    image_name = "dbt-electricity"

    registry_host = f"{region}-docker.pkg.dev"
    image_tag = f"{registry_host}/{project_id}/{repository}/{image_name}:latest"

    print(f"--- Cloud Run Job デプロイ開始: {job_name} ---")

    # 3. gcloud run jobs deploy コマンドの組み立て
    env_vars_to_set = f"GCP_PROJECT_ID={project_id}"

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
        "--project",
        project_id,
        "--service-account",
        service_account,
        "--set-env-vars",
        env_vars_to_set,
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
        raise SystemExit(result.returncode)

    print(f"✨ Cloud Run Job '{job_name}' のデプロイが完了しました！")
    print(f"👉 実行コマンド例: gcloud run jobs execute {job_name} --region {region}")


if __name__ == "__main__":
    main()