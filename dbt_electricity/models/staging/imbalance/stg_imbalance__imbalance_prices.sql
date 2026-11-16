select
  safe.parse_date('%Y%m%d', target_date) as target_date,
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
  kyushu
from
{% if flags.FULL_REFRESH %}
  {{ source('imbalance', 'imbalance_prices_history_ext') }}
{% else %}
  {{ source('imbalance', 'imbalance_prices_latest_ext') }}
{% endif %}