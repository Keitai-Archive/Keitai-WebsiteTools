import os
from export_ff7sb import export_ff7sb
from export_rockmanx import export_rockmanx

# Define where ALL leaderboard CSVs should be saved
OUTPUT_DIR = r""   # <-- CHANGE THIS PATH

def main():
    print(f"[MASTER] Saving all CSVs to: {OUTPUT_DIR}")

    export_ff7sb(OUTPUT_DIR)
    export_rockmanx(OUTPUT_DIR)

    print("[MASTER] All leaderboards exported successfully.")

if __name__ == "__main__":
    main()
