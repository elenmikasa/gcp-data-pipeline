select
  target_date,
  time_slot,
  case area
    when 'hokkaido' then '01'
    when 'tohoku' then '02'
    when 'tokyo' then '03'
    when 'chubu' then '04'
    when 'hokuriku' then '05'
    when 'kansai' then '06'
    when 'chugoku' then '07'
    when 'shikoku' then '08'
    when 'kyushu' then '09'
  end as area_code,
  'インバランス料金' as price_type,
  price_yen_per_kwh
from {{ ref('stg_imbalance__imbalance_prices') }}
unpivot (
  price_yen_per_kwh for area in (
    hokkaido,
    tohoku,
    tokyo,
    chubu,
    hokuriku,
    kansai,
    chugoku,
    shikoku,
    kyushu
  )
)