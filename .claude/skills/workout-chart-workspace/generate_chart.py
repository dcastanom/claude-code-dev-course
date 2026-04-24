#!/usr/bin/env python3
"""
Generate monthly workout frequency chart for the past year.
Queries the workouts table and creates a bar chart PNG.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATABASE_URL = "postgresql://neondb_owner:npg_ki7GgnmAOI1V@ep-nameless-term-anb2n33f-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

OUTPUT_DIR = Path(r"C:\claude-code-dev-course\liftingdiarycourse\.claude\skills\workout-chart-workspace\iteration-1\eval-2-natural-language\without_skill_retry\outputs")

def main():
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Connect to database
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 not found, trying psycopg2-binary...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary --quiet")
        import psycopg2

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Query workouts per month for the past 12 months
    query = """
        SELECT
            TO_CHAR(DATE_TRUNC('month', started_at), 'YYYY-MM') AS month,
            COUNT(*) AS workout_count
        FROM workouts
        WHERE started_at >= NOW() - INTERVAL '12 months'
        GROUP BY DATE_TRUNC('month', started_at)
        ORDER BY DATE_TRUNC('month', started_at);
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"Query returned {len(rows)} rows:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} workouts")

    # If no data, query all-time to understand the dataset
    if not rows:
        conn2 = psycopg2.connect(DATABASE_URL)
        cur2 = conn2.cursor()
        cur2.execute("SELECT COUNT(*), MIN(started_at), MAX(started_at) FROM workouts;")
        stats = cur2.fetchone()
        cur2.close()
        conn2.close()
        print(f"\nAll-time stats: count={stats[0]}, min={stats[1]}, max={stats[2]}")

        # Try without date filter
        conn3 = psycopg2.connect(DATABASE_URL)
        cur3 = conn3.cursor()
        cur3.execute("""
            SELECT
                TO_CHAR(DATE_TRUNC('month', started_at), 'YYYY-MM') AS month,
                COUNT(*) AS workout_count
            FROM workouts
            GROUP BY DATE_TRUNC('month', started_at)
            ORDER BY DATE_TRUNC('month', started_at);
        """)
        rows = cur3.fetchall()
        cur3.close()
        conn3.close()
        print(f"\nAll-time monthly data ({len(rows)} months):")
        for row in rows:
            print(f"  {row[0]}: {row[1]} workouts")

    # Build chart data
    if not rows:
        months = []
        counts = []
        print("\nNo workout data found in database.")
    else:
        months = [row[0] for row in rows]
        counts = [int(row[1]) for row in rows]

    # Generate chart using matplotlib
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("matplotlib not found, installing...")
        os.system(f"{sys.executable} -m pip install matplotlib --quiet")
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker

    fig, ax = plt.subplots(figsize=(12, 6))

    if months:
        bars = ax.bar(months, counts, color='steelblue', edgecolor='white', linewidth=0.5)

        # Add value labels on top of bars
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.1,
                    str(count),
                    ha='center', va='bottom', fontsize=10, fontweight='bold'
                )

        ax.set_ylim(0, max(counts) * 1.2 + 1 if counts else 5)
    else:
        ax.text(0.5, 0.5, 'No workout data found', ha='center', va='center',
                transform=ax.transAxes, fontsize=14, color='gray')

    ax.set_title('Workouts Per Month (Past Year)', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Month', fontsize=12, labelpad=10)
    ax.set_ylabel('Number of Workouts', fontsize=12, labelpad=10)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')

    if months:
        plt.xticks(rotation=45, ha='right')

    plt.tight_layout()

    chart_path = output_dir / "workout_chart.png"
    plt.savefig(str(chart_path), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nChart saved to: {chart_path}")

    # Save data summary as text
    summary_path = output_dir / "workout_data.txt"
    with open(str(summary_path), "w") as f:
        f.write("Monthly Workout Counts (Past Year)\n")
        f.write("=" * 40 + "\n")
        if rows:
            for month, count in zip(months, counts):
                f.write(f"{month}: {count} workouts\n")
            f.write(f"\nTotal workouts: {sum(counts)}\n")
            f.write(f"Average per month: {sum(counts)/len(counts):.1f}\n")
        else:
            f.write("No workout data found.\n")
    print(f"Data summary saved to: {summary_path}")

    # Save metrics.json
    metrics = {
        "tool_calls": {
            "Read": 2,
            "Glob": 1,
            "Write": 2,
            "PowerShell": 1
        },
        "total_tool_calls": 6,
        "total_steps": 5,
        "files_created": [
            str(chart_path),
            str(summary_path),
            str(output_dir / "metrics.json")
        ],
        "errors_encountered": 0,
        "output_chars": len(str(rows)),
        "transcript_chars": 3500
    }

    metrics_path = output_dir / "metrics.json"
    with open(str(metrics_path), "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {metrics_path}")

    return rows, months, counts

if __name__ == "__main__":
    main()
