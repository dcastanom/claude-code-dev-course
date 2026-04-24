---
name: workout-chart
description: >
  Generates a monthly workout frequency bar chart as a PNG image by querying the project's
  PostgreSQL database. Use this skill whenever the user asks to visualize workout data,
  chart workout history, see how many workouts they've done per month, plot workout frequency,
  or export any chart/graph of their lifting diary data. Trigger even if the user just says
  "show me my workout stats" or "how often have I been working out".
---

# Workout Chart

Generate a bar chart (x = month, y = workout count) for the past 12 months from the Neon
PostgreSQL database and save it as `workout_chart.png`.

## Step 1 — Find DATABASE_URL

Look for the database URL in this order inside the project root (the directory that contains
`package.json`):

1. `.env.local`  ← Next.js convention, check this first
2. `.env`

Read whichever file exists and extract the line that starts with `DATABASE_URL=`.
Strip surrounding quotes if present.

If neither file exists, stop and tell the user:

> "No `.env.local` or `.env` file found in the project root. Please create one with a
> `DATABASE_URL=<your-neon-connection-string>` line."

## Step 2 — Check Python dependencies

Run a quick check:

```bash
python -c "import psycopg2, matplotlib" 2>&1
```

If either import fails, tell the user which package is missing and how to install it:

```
pip install psycopg2-binary matplotlib
```

Then stop — do not try to run the chart script until dependencies are available.

## Step 3 — Run the bundled chart script

The script lives at `scripts/generate_chart.py` relative to this SKILL.md file.
Pass `DATABASE_URL` as an environment variable:

```bash
DATABASE_URL="<url>" python "<absolute-path-to-scripts/generate_chart.py>"
```

The script will:
- Connect to the database
- Query the `workouts` table for entries in the past 12 months (using the `started_at` column)
- Fill in months with zero workouts so there are no gaps in the chart
- Save `workout_chart.png` in the **current working directory** (wherever the user's shell is)

## Step 4 — Report success

After the script prints `Chart saved to: <path>`, tell the user:

> "Done! Your workout chart has been saved to `<path>`."

If the script exits with a non-zero code, show the error output and suggest fixes based on
what failed (connection error → check DATABASE_URL; import error → install missing package).

## Schema reference

- Table: `workouts`
- Date column: `started_at` (timestamp with time zone)
- The script queries `started_at >= NOW() - INTERVAL '1 year'` and groups by month.
