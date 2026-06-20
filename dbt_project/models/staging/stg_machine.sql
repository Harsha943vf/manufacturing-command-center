select
    machine_id,
    line_id,
    machine_type,
    cast(install_date as date) as install_date,
    cast(baseline_failure_rate as double) as baseline_failure_rate,
    cast(rotational_speed_rpm_mean as double) as rotational_speed_rpm_mean,
    cast(torque_nm_mean as double) as torque_nm_mean
from {{ ref('dim_machine') }}
