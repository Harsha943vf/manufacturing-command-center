# Demonstrating SCD Type 2 (Slowly Changing Dimensions) With a Static Dataset

`dbt snapshot` captures history by comparing the *current* state of a source table against
what was captured on the *previous* snapshot run. With a one-time synthetic dataset, there's
no natural "previous state" yet — so here's how to demonstrate the mechanic convincingly for
a portfolio (this is also exactly how you'd test SCD2 logic in a real project before going live):

## Steps

1. Run the initial snapshot to establish a baseline:
   ```bash
   dbt snapshot
   ```
   This creates `snapshots.supplier_reliability_snapshot` with `dbt_valid_from` / `dbt_valid_to`
   columns, all currently open (`dbt_valid_to IS NULL`).

2. Manually simulate a real-world change — e.g., Supplier S11 (Monterrey Metal Supply) gets
   downgraded after a string of late deliveries. Edit `seeds/dim_supplier.csv` and change
   `S11`'s `on_time_delivery_rate` from `0.721` to `0.55`, then:
   ```bash
   dbt seed --select dim_supplier
   dbt run --select stg_supplier
   dbt snapshot
   ```

3. Query the snapshot table:
   ```sql
   select supplier_id, on_time_delivery_rate, dbt_valid_from, dbt_valid_to
   from snapshots.supplier_reliability_snapshot
   where supplier_id = 'S11'
   order by dbt_valid_from;
   ```
   You'll see **two rows** for S11 — the original record now has a closed `dbt_valid_to`
   timestamp, and a new row is open with the updated rate. This is the SCD Type 2 pattern:
   full history preserved, nothing overwritten.

## Why this matters in an interview
You can say: *"I tested the SCD2 logic by simulating a supplier reliability change and verified
dbt correctly closed out the old record and opened a new one — which is exactly the pattern
you'd want before trusting this in a production warehouse where supplier ratings, machine
ownership, or line configurations change over time."*

That sentence alone demonstrates you understand *why* SCD2 exists, not just that you copy-pasted
a snapshot block.
