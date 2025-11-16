import csv
import os
from db_shared import get_connection

GAME_NAME = "FF7SB"
DB_NAME = ""
TABLE_NAME = ""
MAP_IDS = [1, 3, 5]
USERNAME_COLUMN = "name"   # change to "playername" if needed


def fetch_map(conn, map_id):
    query = """
        SELECT *
        FROM (
            SELECT DISTINCT ON ({user_col}) *
            FROM {table}
            WHERE map = %s
            ORDER BY {user_col}, run_time ASC
        ) AS sub
        ORDER BY run_time ASC
        LIMIT 10;
    """.format(
        user_col=USERNAME_COLUMN,
        table=TABLE_NAME
    )

    with conn.cursor() as cur:
        cur.execute(query, (map_id,))
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

    # Strip 'uid'
    if "uid" in headers:
        idx = headers.index("uid")
        headers = [h for i, h in enumerate(headers) if i != idx]
        rows = [
            tuple(v for i, v in enumerate(row) if i != idx)
            for row in rows
        ]

    # Add map_id at the end
    headers.append("map_id")
    rows = [tuple(list(r) + [map_id]) for r in rows]

    return headers, rows


def export_ff7sb(output_dir):
    """
    Export all maps into a single ff7sb.csv inside the given output_dir.
    """
    print(f"[FF7SB] Connecting to DB '{DB_NAME}'...")
    conn = get_connection(DB_NAME)

    all_rows = []
    headers = None

    try:
        for map_id in MAP_IDS:
            print(f"[FF7SB] Fetching map {map_id}...")
            hdrs, rows = fetch_map(conn, map_id)

            if headers is None:
                headers = hdrs

            all_rows.extend(rows)
    finally:
        conn.close()
        print("[FF7SB] Database connection closed.")

    if headers is None:
        print("[FF7SB] No data returned — CSV not written.")
        return

    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, f"{GAME_NAME.lower()}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_rows)

    print(f"[FF7SB] Wrote {len(all_rows)} rows → {csv_path}")
