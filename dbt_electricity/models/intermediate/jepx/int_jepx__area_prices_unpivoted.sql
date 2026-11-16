select
  delivery_date,
  time_slot,
  case area
    when 'hokkaido_price_yen_per_kwh' then '01'
    when 'tohoku_price_yen_per_kwh' then '02'
    when 'tokyo_price_yen_per_kwh' then '03'
    when 'chubu_price_yen_per_kwh' then '04'
    when 'hokuriku_price_yen_per_kwh' then '05'
    when 'kansai_price_yen_per_kwh' then '06'
    when 'chugoku_price_yen_per_kwh' then '07'
    when 'shikoku_price_yen_per_kwh' then '08'
    when 'kyushu_price_yen_per_kwh' then '09'
  end as area_code,
  'エリアプライス' as price_type,
  price_yen_per_kwh
from {{ ref('stg_jepx__spot_summary') }}
unpivot (
  price_yen_per_kwh for area in (
    hokkaido_price_yen_per_kwh,
    tohoku_price_yen_per_kwh,
    tokyo_price_yen_per_kwh,
    chubu_price_yen_per_kwh,
    hokuriku_price_yen_per_kwh,
    kansai_price_yen_per_kwh,
    chugoku_price_yen_per_kwh,
    shikoku_price_yen_per_kwh,
    kyushu_price_yen_per_kwh
  )
)
