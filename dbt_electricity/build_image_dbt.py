"""dbt コンテナイメージを Cloud Build でビルドするスクリプト"""

import sys
from pathlib import Path

# dbt_electricity/build_image_dbt.py から見て 1 つ上がプロジェクトルート（jepx_imbalance）
project_root = Path(__file__).resolve().parent.parent
# sys.path には実行スクリプトのフォルダや標準/外部ライブラリパスなどがリスト(list[str])で格納されている
# 未登録ならプロジェクトルートを先頭(index 0)に挿入し、utils 配下を優先探索させる
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.cloud_build import run_cloud_build


def main() -> None:
    target_dir = Path(__file__).resolve().parent
    run_cloud_build(
        image_name="dbt-electricity",
        target_dir=target_dir,
    )


if __name__ == "__main__":
    main()