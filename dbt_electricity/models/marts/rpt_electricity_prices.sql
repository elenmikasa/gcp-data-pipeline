{{ config(materialized='view') }}

select
  f.target_date,
  f.time_slot,
  t.time_label,
  f.area_code,
  a.area_name,
  f.price_type,
  f.price_yen_per_kwh
from {{ ref('fct_electricity_prices') }} as f
left join {{ ref('dim_areas') }} as a
  on f.area_code = a.area_code
left join {{ ref('dim_time_slots') }} as t
  on f.time_slot = t.time_slot