"""Cloud Build 実行用の共通関数モジュール"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv


def run_cloud_build(
    image_name: str,
    target_dir: str | Path,
    image_tag: str = "latest",
) -> str:
    """`.env` を読み込み、指定したビルド対象ディレクトリで Cloud Build を実行する。

    Args:
        image_name: Artifact Registry 上のイメージ名（例: "dbt-electricity"）
        target_dir: Dockerfile が置かれたビルド対象ディレクトリのパス
        image_tag: イメージタグ（デフォルト: "latest"）

    Returns:
        ビルド・プッシュした完全なコンテナイメージタグ文字列
    """
    # utils/cloud_build.py から見て 2 つ上の階層をプロジェクトルートとする
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path)

    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION", "asia-northeast1")
    repository = os.getenv("ARTIFACT_REGISTRY_REPOSITORY")

    if not project_id:
        raise ValueError("環境変数 GCP_PROJECT_ID が設定されていません。")
    if not repository:
        raise ValueError("環境変数 ARTIFACT_REGISTRY_REPOSITORY が設定されていません。")

    # target_dir が相対パスの場合は project_root 基準、絶対パスならそのまま解決する
    context_path = Path(target_dir)
    if not context_path.is_absolute():
        context_path = (project_root / context_path).resolve()
    else:
        context_path = context_path.resolve()

    if not context_path.exists():
        raise FileNotFoundError(f"ビルド対象ディレクトリが見つかりません: {context_path}")

    registry_host = f"{region}-docker.pkg.dev"
    container_image_tag = f"{registry_host}/{project_id}/{repository}/{image_name}:{image_tag}"

    print("--- Cloud Build 開始 ---")
    print(f"Image Tag  : {container_image_tag}")
    print(f"Context    : {context_path}")

    cmd = [
        "gcloud",
        "builds",
        "submit",
        "--tag",
        container_image_tag,
        str(context_path),
    ]

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print("❌ Cloud Build に失敗しました。")
        sys.exit(result.returncode)

    print("✨ Cloud Build が正常に完了しました！")
    return container_image_tag