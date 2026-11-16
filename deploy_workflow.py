#!/usr/bin/env python3
"""Cloud Workflows のみをデプロイするスクリプト。"""

import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "asia-northeast1")
WORKFLOW_NAME = "power-price-etl-workflow"
SERVICE_ACCOUNT = os.getenv("WORKFLOW_SERVICE_ACCOUNT")


def main() -> None:
    if not PROJECT_ID or not SERVICE_ACCOUNT:
        print("❌ エラー: .env に GCP_PROJECT_ID または WORKFLOW_SERVICE_ACCOUNT が設定されていません。", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 workflow.yaml のデプロイを開始します (対象: {WORKFLOW_NAME})")

    cmd = [
        "gcloud", "workflows", "deploy", WORKFLOW_NAME,
        f"--project={PROJECT_ID}",
        f"--location={REGION}",
        "--source=workflow.yaml",
        f"--service-account={SERVICE_ACCOUNT}",
        # 👇 ワークフロー実行環境に環境変数をセットするオプションを追加
        f"--set-env-vars=PROJECT_ID={PROJECT_ID},REGION={REGION}",
    ]

    print(f"▶ 実行中: {' '.join(cmd)}")
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print("❌ デプロイに失敗しました。", file=sys.stderr)
        sys.exit(result.returncode)

    print("🎉 workflow.yaml のデプロイが完了しました！")


if __name__ == "__main__":
    main()