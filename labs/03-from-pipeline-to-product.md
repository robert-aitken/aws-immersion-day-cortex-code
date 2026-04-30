# Lab 03: From Pipeline to Product

**Duration**: 45-60 minutes

> **Prerequisite**: Complete [Lab 02](02-fix-the-pipeline.md) first — you need a working marts layer.

## Objective

You just fixed a broken dbt pipeline and now have a clean analytics layer in the `MARTS` schema. In this lab you'll turn that pipeline into something a human can actually look at and interact with.

This is a **build challenge**, not a walkthrough. Your goal is to use CoCo CLI to generate a Streamlit app on top of the marts, then optionally level it up with a semantic view, a chat interface, or Snowflake-native ML.

> **Prize**: the most impressive Streamlit app at the end of the workshop gets a prize. Impressive is defined by the judging rubric below, not just polish.

## The Challenge

Build a Streamlit app that turns `COCO_WORKSHOP.MARTS` into a useful data product.

**Baseline requirement (Bronze tier)**:

- Deployed as a **Streamlit in Snowflake (SiS)** app using the container runtime
- At least 2 meaningful charts backed by `fct_orders` and/or `dim_customers`
- At least 1 interactive filter (region, category, date range, customer segment, etc.)
- One clearly labeled "insight" section — a narrative, a KPI summary, or a "what to do next" panel

How you get there is up to you. Pick a persona and an angle. Some ideas:

- **Executive Briefing** — clean CEO dashboard with top-line KPIs, trend, and regional mix
- **Sales Hunter** — surface the biggest expansion opportunities in the customer base
- **Category Investigator** — find underperforming categories or regions
- **Customer Copilot** — natural-language chat over customer and order metrics
- **Revenue Game Day** — spot unusual shifts or outliers quickly
- **Ops Cockpit** — a focused single-screen view of order volume, AOV, and revenue trends

Two people picking different personas will build very different apps on the same data. That's the point.

## Suggested Starter Prompts

Pick one of these to give CoCo and then iterate. Don't just accept the first version — push it.

```
Build a Streamlit in Snowflake app that connects using connection DEMO and
queries COCO_WORKSHOP.MARTS. The app should help a sales leader track revenue,
top customers, and weak regions. Deploy it as a SiS app with the container
runtime. Make it feel polished and presentation-ready, with a clear executive
summary at the top.
```

```
Build a Streamlit in Snowflake app aimed at an analyst who wants to find
unusual trends in order volume, average order value, and product category
performance. Include filters for region and category, and a section that
calls out anomalies or outliers it finds in the data. Deploy with the
container runtime.
```

```
Build a Streamlit in Snowflake app with an executive summary, interactive
charts, and a section called "Where to act next". Infer useful opportunities
from the data in COCO_WORKSHOP.MARTS and explain each recommendation in
plain English. Use the container runtime for deployment.
```

```
Create a multi-page Streamlit in Snowflake app over COCO_WORKSHOP.MARTS
with one page per persona: an executive overview, a regional deep dive,
and a customer leaderboard. Add cross-page filters for date range and
region. Deploy with the container runtime.
```

Then keep going. Ask CoCo to restyle it, add narrative copy, add drilldowns, add comparisons, add a sidebar nav. Small iterations produce much better apps than one giant prompt.

## Getting Started

Launch CoCo from your workshop directory:

```bash
cd ~/workshop
cortex -c DEMO
```

Then hand it one of the prompts above and work with it. CoCo should:

1. Read `AGENTS.md` and understand the workshop context
2. Scaffold a `snowflake.yml` + `app.py` (and optionally `requirements.txt`) for a SiS container-runtime app
3. Deploy the app with `snow streamlit deploy -c DEMO --open`
4. Iterate on the app code and redeploy with `snow streamlit deploy -c DEMO --replace`

> ### Why Streamlit in Snowflake, not local?
>
> - **Zero networking setup** — no port-forwarding, no Session Manager tunnels, no firewall rules
> - **Auth handled automatically** — the SiS app runs with the same role and warehouse as your connection
> - **Same place the data lives** — queries stay inside Snowflake, no data leaves the account
> - **Easy to share** — send the instructor a link for judging instead of screen-sharing an EC2 terminal

> [!IMPORTANT]
> ### Container runtime required
>
> When your SiS app is created, make sure CoCo selects the **container runtime** (SPCS-backed), **NOT** the legacy warehouse runtime. The warehouse runtime has a locked, curated Anaconda channel and will fail with `ModuleNotFoundError` on anything outside that set. The container runtime reads `requirements.txt` / `pyproject.toml` directly and can install packages from PyPI.
>
> If you get a package error, this is almost certainly why. Check your `snowflake.yml` — it should include `runtime_name` and `compute_pool` fields.

Here is the `snowflake.yml` pattern your project should use:

```yaml
definition_version: 2
entities:
  workshop_app:
    type: streamlit
    identifier: coco_workshop_app
    query_warehouse: COCO_WORKSHOP_WH
    compute_pool: COCO_WORKSHOP_COMPUTE_POOL
    runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11
    main_file: app.py
    artifacts:
      - app.py
      - requirements.txt
```

Key things to note:
- `runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` — this is what selects the container runtime
- `compute_pool` — required for the container runtime; use the pool your instructor provisioned (check with `SHOW COMPUTE POOLS`)
- `artifacts` — list every file your app needs (pages, data files, etc.)

Deploy with:

```bash
snow streamlit deploy -c DEMO --open
```

Redeploy after edits:

```bash
snow streamlit deploy -c DEMO --replace
```

## Judging Rubric

The winning app will score well across all five dimensions, not just one:

| Dimension | What we're looking for |
|---|---|
| **Clarity** | Can a non-technical person understand it in 30 seconds? |
| **Usefulness** | Does it answer a real business question, not just show data? |
| **Creativity** | Is it more than a default dashboard? Did you pick a persona and commit to it? |
| **Interaction** | Filters, drilldowns, comparisons, or a chat interface — not just static charts |
| **Finish** | Does it feel complete? Clean layout, sensible defaults, helpful copy |

## The Bounty Hunt

There are 5 deliberately planted insights hiding in the dataset. Each one is a clear, unambiguous business finding that is invisible from a raw `SELECT *` but obvious from the right chart or aggregate.

**Find them to level up your recognition:**

- Find 3 → eligible for **Silver** recognition
- Find 4 → eligible for **Gold** recognition
- Find 5 → eligible for **Platinum** recognition

Here are the five eggs. The names are evocative, the hints are cryptic. The answers are NOT here — you have to find them.

| # | Name | Hint |
|---|---|---|
| 1 | **The Category Collapse** | Something bad happened mid-2025. A whole product category never recovered. Which one, and when? |
| 2 | **The Silent Star** | One of our four regions looks tiny at first glance. But look closer at growth and order value. The future is not where the revenue is today. |
| 3 | **The VIP Whale Curve** | The revenue distribution is not 80/20. It is much more top-heavy than that. How much of the business really rides on a handful of accounts? |
| 4 | **The Pricing Bug** | A single product has quiet inconsistencies between what we charged per line and what the math says we should have charged. Which product, how often, and how much have we lost? |
| 5 | **The Fraud Cluster** | A small group of customers is responsible for a surprisingly large share of revenue. On closer inspection, their behaviour is... unusual. How many are there, where are they, and how much of our "revenue" might actually be at risk of chargeback? |

**How to hunt:**

- Build charts in your Streamlit app that slice and dice by category, region, customer, and product
- Use Cortex Analyst chat (Gold tier) to ask natural-language questions against the data
- Use Snowflake ML anomaly detection (Platinum tier) to surface statistical outliers — Egg 5 is particularly well-suited to this approach
- Compare line-item math against order totals to catch discrepancies (Egg 4)
- Look at distributions, not just averages — the interesting stuff hides in the tails

No answers are provided in this lab. Finding them is the challenge.

## Bonus Tiers

Baseline gets you Bronze. Each bonus you pull off bumps you a tier. The rubric above still applies — a half-finished semantic view is worth less than a polished Bronze app.

### Silver — Polish and depth

Refine the Bronze app until it feels shippable. Drilldowns, comparison periods, narrative copy, good defaults, a consistent color palette, and a clear story on the landing screen.

Suggested prompt:

```
Refine this Streamlit app so it feels shippable. Add period-over-period
comparisons, consistent styling, helpful default filters, and short narrative
copy on each chart explaining what the viewer should take away.
```

### Gold — Semantic view + chat interface

Define a semantic view over the marts schema and wire a natural-language chat panel into the Streamlit app so users can ask questions instead of clicking filters.

Suggested prompts:

```
Create a Snowflake semantic view over COCO_WORKSHOP.MARTS that defines:
- Dimensions: customer name, region, product category, order date
- Measures: revenue, order count, average order value, customer lifetime value
Save the YAML definition in the repo and create the view in Snowflake.
```

```
Add a chat panel to the Streamlit app that uses Cortex Analyst against the
semantic view we just created. Users should be able to ask questions like
"top 5 regions by revenue last quarter" and get a chart or table back.
```

### Platinum — Snowflake-native ML

Use Snowflake-native ML to add a forecasting or anomaly-detection section to the app. This should feel like a real "deploy and call a model" workflow, not a toy.

Good targets given the available data:

- **Forecast** weekly or monthly revenue by region or category
- **Detect anomalies** in daily order volume or average order value
- **Score** customers or categories that need attention next week

Suggested prompts:

```
Use Snowflake ML Functions to train a forecasting model on weekly revenue
by region from COCO_WORKSHOP.MARTS.FCT_ORDERS. Register the trained model,
then call it in a batch SQL query to produce 8 weeks of forecasted revenue.
Surface the forecast in the Streamlit app with a shaded confidence band.
```

```
Use Snowflake ML Functions to detect anomalies in daily order volume across
the last 12 months. Call the anomaly detector from SQL in a scheduled query
and display flagged days in a "Revenue Game Day" page inside the Streamlit app.
```

```
Use Snowflake Cortex to score each product category by "attention needed"
based on trend, volume, and regional spread. Display the ranked list in the
app with a short plain-English explanation for each category.
```

Avoid framing this as a classic product recommender — the current dataset doesn't have the interaction data to make that interesting. Forecasting and anomaly detection are a much better fit.

## Demo and Vote

When time is called:

1. Each participant gets a short slot to demo their app
2. Everyone votes using the rubric
3. Instructor announces the winner

## What You've Learned

- How to deploy a Streamlit in Snowflake app from CoCo using the container runtime
- How small prompt iterations produce dramatically better apps than one big prompt
- How to layer a semantic view and natural-language chat on top of existing marts
- How to call Snowflake-native ML functions from SQL to add forecasting or anomaly detection
- Why picking a persona first makes the final app much more useful than "build a dashboard"
- How to find non-obvious business insights by combining the right charts, aggregations, and ML techniques

---

**Previous**: [Lab 02: Fix the Pipeline](02-fix-the-pipeline.md) | **Next (advanced)**: [Lab 04: Deploy and Orchestrate](04-deploy-and-orchestrate.md)
