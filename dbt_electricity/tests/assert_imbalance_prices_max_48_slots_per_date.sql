select target_date
from {{ ref('stg_imbalance__imbalance_prices') }}
group by target_date
having count(*) > 48
