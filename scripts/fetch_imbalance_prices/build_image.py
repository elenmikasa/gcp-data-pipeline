"""Cloud Buildでfetch用イメージをビルドし、Artifact Registryへ保存する。"""

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

IMAGE_NAME = "imbalance-fetch"


def main() -> None:
    # .envからCloud BuildとArtifact Registryの設定を読み込む。
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    REGION = os.getenv("GCP_REGION")
    REPOSITORY = os.getenv("ARTIFACT_REGISTRY_REPOSITORY")
    missing = [
        name
        for name, value in (
            ("GCP_PROJECT_ID", PROJECT_ID),
            ("GCP_REGION", REGION),
            ("ARTIFACT_REGISTRY_REPOSITORY", REPOSITORY),
        )
        if not value
    ]
    if missing:
        raise ValueError(f".envに必要な設定がありません: {', '.join(missing)}")

    # Artifact Registryに保存するイメージの完全なURIを組み立てる。
    IMAGE_URI = (
        f"{REGION}-docker.pkg.dev/{PROJECT_ID}/"
        f"{REPOSITORY}/{IMAGE_NAME}:latest"
    )
    # このスクリプトと同じフォルダをビルドコンテキストにする。
    source_dir = Path(__file__).resolve().parent
    # Cloud Buildでビルドし、完成したイメージをArtifact Registryへpushする。
    command = [
        "gcloud.cmd",
        "builds",
        "submit",
        str(source_dir),
        "--project",
        PROJECT_ID,
        "--region",
        REGION,
        "--tag",
        IMAGE_URI,
    ]

    print(f"ビルド・保存するイメージ: {IMAGE_URI}", flush=True)
    subprocess.run(command, check=True)
    print(f"Artifact Registryへ保存しました: {IMAGE_URI}")


if __name__ == "__main__":
    main()
