# Resume & LinkedIn Copy — Final Versions (Using Real Computed Numbers)

These now use the actual numbers your pipeline computed, not placeholder estimates —
more defensible in an interview ("walk me through how you got that number" → you actually can).

---

## Resume Bullets (STAR Format)

- Built a synthetic manufacturing "digital twin" calibrated against real-world failure and
  quality distributions (UCI AI4I 2020 Predictive Maintenance, SECOM Manufacturing datasets)
  and World Bank Logistics Performance Index supplier benchmarks, then engineered a free
  dbt-duckdb pipeline with automated data-quality testing that identified a single supplier
  responsible for **$695K** in downstream production-shortage cost — the largest single risk
  in the network, exceeding the combined impact of the next two highest risks.

- Designed a transparent, weighted Machine Maintenance Risk Score and Supplier Risk Index
  (replacing black-box anomaly detection) and embedded both into a Tableau Public "Command
  Center" dashboard with role-based persona views and an interactive what-if scenario
  simulator, surfacing **$2.8M** in cumulative downtime cost and **$1.2M** in lost production
  revenue across an 18-month simulation window.

---

## LinkedIn / Portfolio Project Description (Short Version)

**Manufacturing Intelligence & Supply Chain Risk Command Center**

Built an end-to-end analytics platform connecting machine health, supplier reliability, and
financial exposure across a simulated 3-plant manufacturing network. The data itself isn't
random — it's a synthetic "digital twin" calibrated against real published statistics from
the UCI AI4I 2020 Predictive Maintenance dataset, the SECOM Manufacturing dataset, and the
World Bank Logistics Performance Index.

The dashboard's biggest finding: a single supplier (representing just 1 of 12 vendors)
accounted for $695K in downstream shortage cost — more than double the next-largest risk —
because severe delivery delays on a critical electronics component repeatedly stalled an
entire production line. That's the kind of insight a purely descriptive dashboard misses,
but a financially-quantified risk ranking catches immediately.

**Stack:** Python (synthetic data generation calibrated to real distributions) → dbt-duckdb
(star schema, SCD2 snapshots, automated testing) → GitHub Actions (orchestration) → Tableau
Public (persona-based dashboards, what-if scenario simulator, 30-day forecast).

🔗 [Your Tableau Public link] · 🔗 [Your GitHub repo]

---

## Interview Talking Points (Practice These)

**"Walk me through your most interesting finding."**
> "I built a risk-scoring layer that ranks both machine failure risk and supplier
> reliability risk on the same dollar scale. The top risk in the whole network turned out
> to be a supplier, not a machine — a Vietnam-based electronics supplier whose delivery
> delays caused $695K in downstream shortage cost, more than the next two risks combined.
> If I'd only built an OEE dashboard, that would have looked like a generic line-3 downtime
> problem. The supplier risk index is what actually pointed at the root cause."

**"How do you know your synthetic data is realistic?"**
> "I didn't generate it randomly. The machine failure rate is calibrated to the UCI AI4I
> 2020 dataset's published 3.39% failure rate — mine landed at 3.16% on the actual run,
> which is within normal sampling variance. Supplier reliability is calibrated to World
> Bank Logistics Performance Index scores by region, and it shows the expected pattern —
> Germany-region suppliers outperform Mexico-region suppliers, which matches real published
> logistics data, not an assumption I made up."

**"What would you do differently in production?"**
> "Three things: trace defects back to specific material batches instead of just
> production-run level, which would let the Supplier Risk Index include an actual quality
> factor instead of the downstream-impact proxy I used; pull live FRED industrial production
> data instead of my placeholder trend constant; and move the orchestration from GitHub
> Actions to something with better dependency management once the pipeline has more than a
> handful of models, like Dagster or a managed Airflow."
