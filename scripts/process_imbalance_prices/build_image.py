""" .env から設定を読み込み、Cloud Build を実行するスクリプト """

import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def main() -> None:
    # プロジェクトのルートにある .env ファイルを読み込む
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # .env から必要な設定を読み込む
    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION", "asia-northeast1")
    repository = os.getenv("ARTIFACT_REGISTRY_REPOSITORY")

    if not project_id:
        raise ValueError("環境変数 GCP_PROJECT_ID が設定されていません。")
    if not repository:
        raise ValueError("環境変数 ARTIFACT_REGISTRY_REPOSITORY が設定されていません。")

    # --- 各要素を変数に定義する ---
    registry_host = f"{region}-docker.pkg.dev"
    image_name = "process-imbalance-prices"
    image_tag = "latest"

    # 変数を組み合わせて、完全なイメージタグ文字列を組み立てる
    container_image_tag = f"{registry_host}/{project_id}/{repository}/{image_name}:{image_tag}"

    # Dockerfile があるディレクトリ（scripts/process_imbalance_prices）を指定
    target_dir = Path(__file__).resolve().parent

    print("--- Cloud Build 開始 ---")
    print(f"Project ID : {project_id}")
    print(f"Repository : {repository}")
    print(f"Image Tag  : {container_image_tag}")
    print(f"Context    : {target_dir}")

    # gcloud builds submit コマンドを組み立てて実行
    cmd = [
        "gcloud",
        "builds",
        "submit",
        "--tag",
        container_image_tag,
        str(target_dir),
    ]

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print("❌ Cloud Build に失敗しました。")
        exit(result.returncode)
    else:
        print("✨ Cloud Build が正常に完了しました！")

if __name__ == "__main__":
    main()