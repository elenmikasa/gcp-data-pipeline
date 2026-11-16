
select
  safe.parse_date('%Y/%m/%d', delivery_date) as delivery_date,
  lpad(cast(time_slot as string), 2, '0') as time_slot,
  sell_bid_volume_kwh,
  buy_bid_volume_kwh,
  contract_volume_kwh,
  system_price_yen_per_kwh,
  hokkaido_price_yen_per_kwh,
  tohoku_price_yen_per_kwh,
  tokyo_price_yen_per_kwh,
  chubu_price_yen_per_kwh,
  hokuriku_price_yen_per_kwh,
  kansai_price_yen_per_kwh,
  chugoku_price_yen_per_kwh,
  shikoku_price_yen_per_kwh,
  kyushu_price_yen_per_kwh,
  sell_block_bid_volume_kwh,
  sell_block_contract_volume_kwh,
  buy_block_bid_volume_kwh,
  buy_block_contract_volume_kwh
from {{ source('jepx', 'spot_summary_ext') }}