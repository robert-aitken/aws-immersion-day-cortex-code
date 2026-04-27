# Lab 03: From Pipeline to Product

**Duration**: 45-60 minutes

## Objective

You just fixed a broken dbt pipeline and now have a clean analytics layer in the `MARTS` schema. In this lab you'll turn that pipeline into something a human can actually look at and interact with.

This is a **build challenge**, not a walkthrough. Your goal is to use CoCo CLI to generate a Streamlit app on top of the marts, then optionally level it up with a semantic view, a chat interface, or Snowflake-native ML.

> **Prize**: the most impressive Streamlit app at the end of the workshop gets a prize. Impressive is defined by the judging rubric below, not just polish.

## The Challenge

Build a Streamlit app that turns `COCO_WORKSHOP.MARTS` into a useful data product.

**Baseline requirement (Bronze tier)**:

- Runs locally on the EC2 jumphost (or Streamlit in Snowflake if you prefer)
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
Build a Streamlit app in ~/workshop/app/app.py that connects to Snowflake
using connection DEMO and queries COCO_WORKSHOP.MARTS. The app should help
a sales leader track revenue, top customers, and weak regions. Make it feel
polished and presentation-ready, with a clear executive summary at the top.
```

```
Build a Streamlit app aimed at an analyst who wants to find unusual trends
in order volume, average order value, and product category performance.
Include filters for region and category, and a section that calls out
anomalies or outliers it finds in the data.
```

```
Build a Streamlit app with an executive summary, interactive charts, and a
section called "Where to act next". Infer useful opportunities from the
data in COCO_WORKSHOP.MARTS and explain each recommendation in plain English.
```

```
Create a multi-page Streamlit app over COCO_WORKSHOP.MARTS with one page per
persona: an executive overview, a regional deep dive, and a customer
leaderboard. Add cross-page filters for date range and region.
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
2. Generate a `requirements.txt` or install into the existing environment
3. Scaffold `app/app.py` (or similar) that uses `snowflake.connector` with connection `DEMO`
4. Run the app and open it in a browser tab

If you're running on the EC2 jumphost, you may need to either port-forward via Session Manager or run the app inside Streamlit in Snowflake. Ask CoCo for the simplest option in your environment.

## Judging Rubric

The winning app will score well across all five dimensions, not just one:

| Dimension | What we're looking for |
|---|---|
| **Clarity** | Can a non-technical person understand it in 30 seconds? |
| **Usefulness** | Does it answer a real business question, not just show data? |
| **Creativity** | Is it more than a default dashboard? Did you pick a persona and commit to it? |
| **Interaction** | Filters, drilldowns, comparisons, or a chat interface — not just static charts |
| **Finish** | Does it feel complete? Clean layout, sensible defaults, helpful copy |

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

- How to go from a clean marts layer to a user-facing data product using CoCo
- How small prompt iterations produce dramatically better apps than one big prompt
- How to layer a semantic view and natural-language chat on top of existing marts
- How to call Snowflake-native ML functions from SQL to add forecasting or anomaly detection
- Why picking a persona first makes the final app much more useful than "build a dashboard"
