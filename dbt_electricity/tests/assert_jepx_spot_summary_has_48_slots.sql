select delivery_date
from {{ ref('stg_jepx__spot_summary') }}
group by delivery_date
having 
    -- 日付ごとの行数が48件あることを確認する
    count(*) != 48
    -- コマ番号が1〜48の範囲外の行がないことを確認する
    or countif(
      safe_cast(time_slot as int64) not between 1 and 48
    ) > 0