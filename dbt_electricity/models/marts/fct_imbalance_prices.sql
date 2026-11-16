{{
  config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['target_date', 'time_slot']
  )
}}

select
  target_date,
  time_slot,
  time_start,
  time_end,
  hokkaido,
  tohoku,
  tokyo,
  chubu,
  hokuriku,
  kansai,
  chugoku,
  shikoku,
  kyushu,
  current_datetime('Asia/Tokyo') as updated_at_jst
from {{ ref('stg_imbalance__imbalance_prices') }}
