# Phase 2: Tableau Public Build Guide
### Copy-paste-ready calculated fields, parameters, and page layouts

This is the production deliverable — the HTML file is a working prototype/spec to validate
the design, but Tableau Public is what goes on your resume and gets shared with recruiters.

## 0. Setup
1. Run the Phase 1 pipeline (`docs/mac_build_guide.md`) through `export_marts_to_csv.py`.
2. Open Tableau Public Desktop → Connect → Text File → select each CSV in `tableau_extracts/`.
3. You'll have these data sources: `fct_oee_daily`, `fct_production_run_enriched`,
   `dim_machine_risk_score`, `dim_supplier_risk_score`, `fct_forecast_30day`,
   `fct_command_center_top_risks`. Also pull in `dim_plant.csv`, `dim_material.csv`,
   `dim_supplier.csv` from `outputs/` directly for the network page.
4. Join `fct_oee_daily` to `dim_plant` on `plant_id` for plant names.

---

## Page 1 — Plant Overview

**Calculated Fields:**
```
// Company Avg OEE (table calc, window avg)
WINDOW_AVG(AVG([oee]))

// Benchmark vs Target
IF [oee] >= 0.85 THEN "Above Target" ELSE "Below Target" END
```

**Layout:** Horizontal bar chart, one bar per plant, OEE on the axis. Add a reference line
at 0.85 (Analytics pane → Reference Line → Constant 0.85, label "Target"). Add a second
reference line for Company Average (Analytics pane → Reference Line → Average). Color bars
by the Benchmark field (green/amber). Three KPI cards above using BANs (Big Ass Numbers):
Company Avg OEE, Total Downtime Cost (SUM of `downtime_cost_usd` from `fct_oee_daily`),
Total Lost Production Revenue (SUM of `lost_production_revenue_usd`).

---

## Page 2 — Machine Risk Scorecard

**Source:** `dim_machine_risk_score.csv` (already has `machine_risk_score` precomputed by dbt).

**Calculated Field — Risk Tier (for color):**
```
IF [machine_risk_score] >= 70 THEN "High"
ELSEIF [machine_risk_score] >= 40 THEN "Medium"
ELSE "Low" END
```

**Layout:** Horizontal bar chart sorted descending by `machine_risk_score`, one bar per
machine, colored by Risk Tier (Red/Amber/Green — set custom colors to match your palette).
Add `total_downtime_minutes` as a tooltip field. Add a calculated **Recommended Action**
field:
```
IF [machine_risk_score] >= 80 THEN "Schedule maintenance within 48 hrs"
ELSEIF [machine_risk_score] >= 50 THEN "Add to next maintenance window"
ELSE "Monitor" END
```
Show this as a label or in a separate text table next to the bar chart.

---

## Page 3 — Supplier & Material Flow Network

Tableau doesn't have a native Sankey/network chart, so build this with a **dual-axis
"connector" technique** — or, simpler and more reliable for a portfolio piece, use a
**highlight table / heatmap** crossing Supplier × Material × Line, colored by
`supplier_risk_score`, with a dashboard **Highlight Action**: clicking a supplier highlights
every row (material/line) it touches.

**Steps:**
1. Build a table: Rows = Supplier Name, Columns = Material Name, Color = `supplier_risk_score`.
2. Add `line_name` and `plant_id` as additional row fields so the downstream chain is visible.
3. Dashboard → Actions → Add Action → Highlight → Source: this sheet → Target: this sheet
   (self-highlight) → Run on Select. Now clicking a supplier highlights its full chain.
4. *(Stretch goal, if you want a true network diagram):* Tableau Public supports the free
   **Sankey chart template** from the Tableau community (search "Tableau Sankey template
   workbook" — download, replace the sample data with your supplier/material/line fields,
   following the polygon-building technique in that template). This is more work but is a
   genuine standout visual if you have the time.

---

## Page 4 — Production Capacity Forecast

**Source:** `fct_forecast_30day.csv` (already computed by dbt — don't use Tableau's
built-in forecasting feature here, since you already have a transparent SQL-computed trend).

**Layout:** Line chart, X = `forecast_date`, Y = `forecasted_oee`. Use a calculated field to
distinguish historical vs. forecasted:
```
// In a unioned view with fct_oee_daily, or just style the forecast line distinctly:
IF [forecast_date] <= TODAY() THEN "Actual" ELSE "Forecast" END
```
Color "Actual" solid steel-blue, "Forecast" dashed amber (Format → Lines → dashed pattern).
Add a reference line at 0.85 (target). Add two BANs below: "Forecasted OEE (next 30d, avg)"
and "Expected Lost Production (units)" from `forecasted_throughput_units` vs. ideal rate.

---

## Page 5 — Scenario Simulator (the standout feature)

This uses Tableau's native **Parameters** — the direct equivalent of Power BI's
What-If Parameters, fully free in Tableau Public.

**Create 3 Parameters:**
1. `Supplier Failure Severity` — Integer, range 0–100, step 5, current value 30 (display as %)
2. `OEE Improvement Target` — Float, range 0–5, step 0.5, current value 2.0 (display as %)
3. `Machine Downtime Duration (hrs)` — Integer, range 0–72, step 4, current value 8

**Calculated Fields using the parameters:**
```
// Supplier Failure Revenue Impact
[Supplier Failure Severity] / 100.0 * 
{ FIXED : MAX(IF [supplier_risk_score] = { FIXED : MAX([supplier_risk_score]) } 
  THEN [total_shortage_cost_usd] END) }

// (Simpler alternative if the nested FIXED above gives you trouble in Tableau Public:
//  just reference your top supplier's shortage cost as a hardcoded benchmark constant,
//  documented inline as "calibrated from dim_supplier_risk_score.csv":)
[Supplier Failure Severity] / 100.0 * 695400   

// Added Annual Capacity from OEE Gain
[OEE Improvement Target] / 100.0 * { FIXED : SUM([lost_production_revenue_usd]) } * 8

// Estimated Production Delay Cost
[Machine Downtime Duration (hrs)] * 60 / 480.0 * 350 * 40
```

**Layout:** Place all 3 parameter controls on the dashboard (right-click each parameter in
the Data pane → Show Parameter). Next to each, a BAN showing the corresponding calculated
field, formatted as currency. This is literally a live "what happens if..." calculator —
walk through it in your portfolio video by dragging a slider and watching the dollar figure
move in real time.

---

## Page 6 — Operations Command Center

**Source:** `fct_command_center_top_risks.csv` (already ranked by dbt).

**Layout:** A simple, clean table — this page should look like a memo, not a chart:
Rank | Risk Type | Description | Risk Score | $ Impact | Recommended Action.
Color the Risk Score column with a diverging color (KPI-style circles: Tableau → right-click
the Risk Score field → Default Properties → or use a calculated field for a 🔴🟡🟢 emoji/text
badge if you want zero-code visual color-coding). Sort descending by `estimated_financial_impact_usd`.
Add a dashboard filter action so clicking a row on this page jumps to the relevant Machine
Risk or Supplier Network page (Dashboard → Actions → Filter, target the other sheet).

---

## Page 7 — Data Governance & Pipeline Health

**Source:** This page is the one place where you're showcasing *process*, not just data.
If you've installed Elementary (see `dbt_project/packages.yml`), export its summary tables
(`elementary.dbt_run_results`, `elementary.dbt_tests`) to CSV the same way you exported the
marts, and build simple KPI tiles: Data Freshness (MAX of a run timestamp), Test Pass Rate
(COUNT tests passed / COUNT total), Failed Runs (last 30 days). If you haven't gotten
Elementary running yet, it's fine to manually log a small `pipeline_log.csv` with a few rows
you update by hand for now — be upfront that this page is illustrative until Elementary is
fully wired in, and that honesty is itself a good interview answer ("here's what's live vs.
what I've architected for and am still wiring up").

---

## Persona Views (Page Filters, Not Separate Workbooks)

Build one workbook. On the **Command Center** and **Plant Overview** dashboards, add a
**Parameter** called `Persona View` (string, values: Executive / Operations / Procurement /
Finance). Use it in a calculated field to filter which rows/KPIs show:
```
CASE [Persona View]
WHEN "Operations" THEN IF [risk_type]="Machine Risk" THEN 1 ELSE 0 END
WHEN "Procurement" THEN IF [risk_type]="Supplier Risk" THEN 1 ELSE 0 END
ELSE 1
END
```
Drag this calculated field to the Filters shelf, set it to show only `1`. Show the Persona
View parameter as a set of buttons at the top of the dashboard — this is your role-switcher.

---

## Publishing
File → Save to Tableau Public As... → sign in with your free Tableau Public account → this
gives you a public URL you can put directly on your resume/LinkedIn (e.g.
`public.tableau.com/app/profile/yourname/viz/ManufacturingCommandCenter`). This is genuinely
better than a .pbix file for a portfolio, since anyone can click and interact with it without
installing anything.

## When You Hit a Wall
Nested `FIXED` LOD calculations in Tableau can be finicky on first attempt — if a formula
above throws an error, simplify to a hardcoded benchmark constant (clearly commented) first,
get the dashboard working end-to-end, then come back and make it fully dynamic. A working
simple version beats a broken sophisticated one every time you're showing this in an interview.
