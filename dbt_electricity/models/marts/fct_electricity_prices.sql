{{
  config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['target_date', 'time_slot', 'area_code', 'price_type']
  )
}}

with jepx_prices as (
  select
    delivery_date as target_date,
    time_slot,
    area_code,
    price_type,
    price_yen_per_kwh
  from {{ ref('int_jepx__area_prices_unpivoted') }}

{% if is_incremental() %}
  where delivery_date >= (
    select coalesce(max(target_date), date '1900-01-01')
    from {{ this }}
  )
{% endif %}
),
imbalance_prices as (
  select
    target_date,
    time_slot,
    area_code,
    price_type,
    price_yen_per_kwh
  from {{ ref('int_imbalance__imbalance_prices_unpivoted') }}
)

select * from jepx_prices

union all

select * from imbalance_prices