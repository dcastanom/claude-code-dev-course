"""
Queries the workouts table for the past 12 months and saves a bar chart as workout_chart.png.
Usage: DATABASE_URL=<url> python generate_chart.py [output_path]
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from collections import OrderedDict

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 is not installed.")
    print("Install it with:  pip install psycopg2-binary")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend, no display needed
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("ERROR: matplotlib is not installed.")
    print("Install it with:  pip install matplotlib")
    sys.exit(1)

# --- connection ---
# DATABASE_URL must come from the environment (read from .env/.env.local by the caller).
# Optional positional arg: sys.argv[1] = output path for the PNG.
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL not set and not passed as argument.")
    sys.exit(1)

try:
    conn = psycopg2.connect(database_url)
except Exception as e:
    print(f"ERROR: Could not connect to database: {e}")
    sys.exit(1)

# --- query ---
now = datetime.now(timezone.utc)
one_year_ago = now - timedelta(days=365)

cursor = conn.cursor()
cursor.execute(
    """
    SELECT DATE_TRUNC('month', started_at) AS month, COUNT(*) AS cnt
    FROM workouts
    WHERE started_at >= %s
    GROUP BY 1
    ORDER BY 1
    """,
    (one_year_ago,),
)
rows = cursor.fetchall()
conn.close()

# --- fill every month in range with 0 so gaps show ---
months: OrderedDict = OrderedDict()
ptr = one_year_ago.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
while ptr <= now:
    months[ptr.replace(tzinfo=None)] = 0
    if ptr.month == 12:
        ptr = ptr.replace(year=ptr.year + 1, month=1)
    else:
        ptr = ptr.replace(month=ptr.month + 1)

for month_ts, cnt in rows:
    key = month_ts.replace(tzinfo=None) if hasattr(month_ts, "tzinfo") else month_ts
    if key in months:
        months[key] = cnt

labels = [m.strftime("%b %Y") for m in months]
counts = list(months.values())

# --- plot ---
fig, ax = plt.subplots(figsize=(14, 6))
bar_color = "#4F46E5"
ax.bar(labels, counts, color=bar_color, edgecolor="white", linewidth=0.5)
ax.set_xlabel("Month", fontsize=12, labelpad=8)
ax.set_ylabel("Number of Workouts", fontsize=12, labelpad=8)
ax.set_title("Workouts per Month — Past 12 Months", fontsize=14, fontweight="bold", pad=14)
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.xticks(rotation=45, ha="right", fontsize=9)
plt.tight_layout()

output_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "workout_chart.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"Chart saved to: {output_path}")
