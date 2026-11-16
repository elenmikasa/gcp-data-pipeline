

### Seedの実行

すべてのseed CSVを実行し、BigQueryの`marts`データセットにテーブルを作成または更新します。

```powershell
dbt seed
```

特定のseedだけを実行する場合：

```powershell
dbt seed --select dim_time_slots
```

```powershell
python -m dbt.cli.main build --select fct_imbalance_prices
```

```powershell
python -m dbt.cli.main test --select path:tests/assert_imbalance_prices_max_48_slots_per_date.sql
```

### インバランス料金モデルの参照先確認

`stg_imbalance__imbalance_prices` は、通常時に `imbalance_prices_latest_ext`、`--full-refresh` 指定時に `imbalance_prices_history_ext` を参照するSQLにコンパイルされます。参照先の切り替えを確認するには、`dbt_electricity` フォルダで次を実行します。

```powershell
python -m dbt.cli.main compile --select stg_imbalance__imbalance_prices
python -m dbt.cli.main compile --full-refresh --select stg_imbalance__imbalance_prices
```

`compile` はSQLの生成・確認のみを行い、BigQuery上のビューやテーブルは作成・更新しません。モデルを実際に更新するには `run` または `build` を実行します。

### 中間モデルの結果確認

中間モデルの結果をテーブルとして作成せずに確認する場合：

```powershell
python -m dbt.cli.main show --select int_imbalance__imbalance_prices_unpivoted --limit 20
```

### レポート用モデルのビルド


```powershell
python -m dbt.cli.main build --select rpt_electricity_prices
```

このコマンドは、`rpt_electricity_prices`とその上流モデルをビルドします。
