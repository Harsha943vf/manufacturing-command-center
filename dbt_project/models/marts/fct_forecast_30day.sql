-- 30-Day Production Capacity Forecast
--
-- Deliberately simple: a linear trend fit over the trailing 60 days of actuals per line,
-- projected forward 30 days. No ML library, no black box -- DuckDB's native regr_slope /
-- regr_intercept aggregate functions do the fitting. This is the right level of sophistication
-- for a descriptive-analytics dashboard with a forward-looking layer; anything more complex
-- would be over-engineering for the business question being asked ("roughly where are we headed
-- if nothing changes?").

with trailing_window as (
    select
        line_id,
        run_date,
        oee,
        units_produced,
        downtime_minutes,
        row_number() over (partition by line_id order by run_date desc) as days_ago
    from {{ ref('fct_oee_daily') }}
),

last_60_days as (
    select * from trailing_window where days_ago <= 60
),

trend_fit as (
    select
        line_id,
        regr_slope(oee, days_ago) as oee_slope,
        regr_intercept(oee, days_ago) as oee_intercept,
        regr_slope(units_produced, days_ago) as throughput_slope,
        regr_intercept(units_produced, days_ago) as throughput_intercept,
        avg(downtime_minutes) as avg_downtime_minutes,
        max(run_date) as last_actual_date
    from last_60_days
    group by line_id
),

forecast_horizon as (
    -- generate 30 forward-looking days_ago values (negative = future, since days_ago counts backward from today)
    select line_id, last_actual_date, -1 * generate_series as days_ahead, oee_slope, oee_intercept,
           throughput_slope, throughput_intercept, avg_downtime_minutes
    from trend_fit, generate_series(1, 30)
)

select
    line_id,
    date_add(last_actual_date, interval (abs(days_ahead)) day) as forecast_date,
    abs(days_ahead) as days_into_future,
    -- note: days_ago in the regression counts backward, so forecasting forward means
    -- plugging in negative days_ago values (i.e. extrapolating past day_ago = 0)
    round(least(1.0, greatest(0.0,
        oee_intercept + oee_slope * days_ahead
    )), 4) as forecasted_oee,
    round(greatest(0.0,
        throughput_intercept + throughput_slope * days_ahead
    ), 0) as forecasted_throughput_units,
    round(avg_downtime_minutes, 1) as expected_downtime_minutes
from forecast_horizon
order by line_id, forecast_date
