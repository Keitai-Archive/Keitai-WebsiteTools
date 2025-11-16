import csv
import os
from db_shared import get_connection

GAME_NAME = "RockmanX"

# Edit these to match your DB
DB_NAME = ""          # e.g. "khak" if that is where the table lives
TABLE_NAME = ""       # table with ip, playername, hiscore, datetime

USERNAME_COLUMN = "playername"
SCORE_COLUMN = "hiscore"


def fetch_top_scores(conn):
    """
    Get top 10 highscores:
      - One best score per playername (highest hiscore)
      - Then top 10 overall, ordered by hiscore DESC
    """
    query = """
        SELECT *
        FROM (
            SELECT DISTINCT ON ({user_col}) *
            FROM {table}
            ORDER BY {user_col}, {score_col} DESC, datetime ASC
        ) AS sub
        ORDER BY {score_col} DESC
        LIMIT 10;
    """.format(
        user_col=USERNAME_COLUMN,
        score_col=SCORE_COLUMN,
        table=TABLE_NAME
    )

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

    # Remove IP column if present
    if "ip" in headers:
        ip_idx = headers.index("ip")
        headers = [h for i, h in enumerate(headers) if i != ip_idx]
        rows = [
            tuple(v for i, v in enumerate(row) if i != ip_idx)
            for row in rows
        ]

    return headers, rows


def export_rockmanx(output_dir):
    """
    Export Rockman X highscores to <output_dir>/rockmanx.csv
    """
    print("[RockmanX] Connecting to DB '{}'...".format(DB_NAME))
    conn = get_connection(DB_NAME)

    try:
        headers, rows = fetch_top_scores(conn)
    finally:
        conn.close()
        print("[RockmanX] Database connection closed.")

    if not rows:
        print("[RockmanX] No data returned — CSV not written.")
        return

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "rockmanx.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print("[RockmanX] Wrote {} rows → {}".format(len(rows), csv_path))
