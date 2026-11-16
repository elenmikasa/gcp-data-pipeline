# Imbalance Price ETL Pipeline (Cloud Run Jobs)

電力市場のインバランス料金CSVデータをAPI経由で自動取得し、Google Cloud Storage (GCS) にアップロードするETLパイプラインです。Python（`httpx`, `google-cloud-storage`）製スクリプトをDockerコンテナ化し、Google Cloud Run Jobsで定期・手動実行します。

---

## 1. アーキテクチャ概要
1. **データ取得**: Pythonスクリプトが指定された年月（`TARGET_MONTHS`）のインバランス料金CSVデータをAPI経由で取得。
2. **ストレージ**: 取得したデータを指定のGCSバケット（`GCS_BUCKET`）へ自動アップロード。
3. **実行環境**: Cloud Run Jobs上でコンテナとして実行。
4. **セキュリティ**: 専用のサービスアカウント（`etl-worker`）を使用し、ログ出力・ジョブ実行権限と、対象GCSバケットへの書き込み権限を最小権限で管理。

---

## 2. ディレクトリ構成
```text
.
├── Dockerfile
├── main.py          # データ取得・GCSアップロード用Pythonスクリプト
├── requirements.txt # 依存ライブラリ (httpx, google-cloud-storage等)
└── README.md
```

---

## 3. 環境変数
Cloud Run Jobsの実行時に、以下の環境変数を設定します。

| 変数名 | 説明 | 例 |
| :--- | :--- | :--- |
| `GCS_BUCKET` | アップロード先のGCSバケット名 | `elenmikasa` |
| `TARGET_MONTHS` | 取得対象の年月 | `202610` |

---

## 4. デプロイ・構築手順

### ① サービスアカウントの作成
1. Google Cloud コンソールから **「IAM と管理」 > 「サービスアカウント」** を開く。
2. 「サービスアカウントを作成」をクリックし、基本情報を入力。
   * **Service account name**: `ETL Worker`
   * **Service account ID**: `etl-worker`
   * **Service account description**: `ETL処理全般用`
3. 「Create and continue」を押し、**「Permissions」** で以下のロールを付与して作成を完了させる。
   * **Logs Writer** (`roles/logging.logWriter`)
      * **意味**: Cloud Logging に対してログ（出力メッセージなど）を書き込む権限。
      * **用途**: コンテナ内で実行されたPythonスクリプトの実行ログや標準出力をGoogle Cloud上で記録・確認するために必要。

   * **Cloud Run Invoker** (`roles/run.invoker`)
      * **意味**: Cloud Run のサービスやジョブを実行（起動・呼び出し）する権限。
      * **用途**: Cloud Scheduler、Cloud Workflows、または手動実行時、ジョブがタスクを安全に起動・制御するために必要。

### ② GCSバケットの権限設定
1. 対象のGCSバケット（`elenmikasa`）の詳細画面を開き、**「権限 (Permissions)」** タブを選択する。
2. **「アクセス権を付与 (Grant access)」** をクリック。
3. **新しいプリンシパル**: 作成したサービスアカウント（`etl-worker@<project-id>.iam.gserviceaccount.com`）を指定。
4. **ロールを選択**: `Cloud Storage` > **「Storage Object Admin（ストレージ オブジェクト管理者）」** を選択して保存。

### ③ DockerイメージのビルドとArtifact Registryへのプッシュ
ローカル環境またはCloud Buildを使用して、コンテナイメージをArtifact Registryに登録します。
```bash
# 例: Cloud Buildでビルドする場合
gcloud builds submit --tag asia-northeast1-docker.pkg.dev/<project-id>/etl-repo/imbalance-fetch:latest .
```

### ④ Cloud Run Jobsの作成・設定
1. Google Cloud コンソールの **「Cloud Run」 > 「ジョブ (Jobs)」** に移動し、「ジョブを作成 (Create job)」をクリック。
2. **コンテナイメージのURL**: Artifact Registryにプッシュした `imbalance-fetch` のイメージを選択。
3. **ジョブ名**: `imbalance-fetch-job` を入力。
4. **リージョン**: `asia-northeast1 (Tokyo)` を選択。
5. **セキュリティ (Security)** タブで、サービスアカウントに `ETL Worker` を選択。
6. **コンテナ (Containers)** タブ内の「Variables & Secrets」で、環境変数に以下を追加。
   * `GCS_BUCKET` = `elenmikasa`
   * `TARGET_MONTHS` = `202610`
7. 「作成 (Create)」をクリック。

---

## 5. 実行方法

### 手動実行
Cloud Run Jobsの詳細画面から **「Execute（実行）」** ボタンをクリックすることで、いつでも手動でジョブを実行できます。
* 成功すると Tasks overview に `1 Succeeded`、終了コード `Last exit code: 0` が表示されます。

### 自動実行（定期実行）の追加
Cloud Schedulerと連携させることで、毎月または毎日自動でジョブをトリガーできます。
1. Cloud Run Jobsの詳細画面上部にある **「Triggers」** タブ、またはCloud Schedulerコンソールからジョブのスケジュール（Cron形式）を設定します。