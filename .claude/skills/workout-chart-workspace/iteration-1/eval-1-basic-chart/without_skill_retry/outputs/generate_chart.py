#!/usr/bin/env python3
"""
Generate a workout frequency chart from the Neon PostgreSQL database.
Queries the workouts table and creates a monthly bar chart saved as PNG.
"""

import os
import sys
import json
from datetime import datetime

# DATABASE_URL from .env
DATABASE_URL = "postgresql://neondb_owner:npg_ki7GgnmAOI1V@ep-nameless-term-anb2n33f-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    start_time = datetime.now()
    tool_calls = 0
    errors = 0
    files_created = []

    print("Connecting to database...")

    try:
        import psycopg2
    except ImportError:
        print("psycopg2 not found, trying psycopg2-binary...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary --quiet")
        import psycopg2

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
    except ImportError:
        print("matplotlib not found, installing...")
        os.system(f"{sys.executable} -m pip install matplotlib --quiet")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker

    # Connect and query
    tool_calls += 1
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    tool_calls += 1
    cur.execute("""
        SELECT
            TO_CHAR(DATE_TRUNC('month', started_at), 'YYYY-MM') AS month,
            COUNT(*) AS workout_count
        FROM workouts
        WHERE started_at IS NOT NULL
        GROUP BY month
        ORDER BY month;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"Query returned {len(rows)} rows.")

    if not rows:
        print("No workout data found. Creating placeholder chart.")
        months = ["No Data"]
        counts = [0]
    else:
        months = [r[0] for r in rows]
        counts = [int(r[1]) for r in rows]

    # Build chart
    tool_calls += 1
    fig, ax = plt.subplots(figsize=(12, 6))

    bar_color = "#4F46E5"  # indigo
    bars = ax.bar(months, counts, color=bar_color, edgecolor="white", linewidth=0.5, width=0.6)

    # Add value labels on bars
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(count),
                ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#1e1b4b"
            )

    ax.set_title("Monthly Workout Frequency", fontsize=16, fontweight="bold", pad=16, color="#1e1b4b")
    ax.set_xlabel("Month", fontsize=12, labelpad=8)
    ax.set_ylabel("Number of Workouts", fontsize=12, labelpad=8)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_facecolor("#f8f7ff")
    fig.patch.set_facecolor("#ffffff")
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#c7d2fe")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "workout_chart.png")
    tool_calls += 1
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    files_created.append(output_path)
    print(f"Chart saved to: {output_path}")

    # Save metrics
    elapsed = (datetime.now() - start_time).total_seconds()
    metrics = {
        "tool_calls": {
            "db_connect": 1,
            "db_query": 1,
            "chart_build": 1,
            "chart_save": 1
        },
        "total_tool_calls": tool_calls,
        "total_steps": 4,
        "files_created": files_created,
        "errors_encountered": errors,
        "output_chars": len(str(rows)),
        "transcript_chars": 0,
        "elapsed_seconds": elapsed,
        "data_rows": len(rows),
        "months": months,
        "counts": counts
    }

    metrics_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    files_created.append(metrics_path)
    print(f"Metrics saved to: {metrics_path}")
    print("Done.")

if __name__ == "__main__":
    main()
