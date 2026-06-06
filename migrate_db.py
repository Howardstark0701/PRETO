"""
Quick migration: add GitHub OAuth columns to users table.
Safe to run multiple times - skips columns that already exist.
"""
import sqlite3
import os
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

DB_PATH = os.path.join(os.path.dirname(__file__), "preto.db")

NEW_COLUMNS = [
    ("github_id",    "VARCHAR(50)"),
    ("github_login", "VARCHAR(100)"),
    ("github_token", "VARCHAR(255)"),
    ("avatar_url",   "VARCHAR(512)"),
]

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    existing = {row[1] for row in cursor.fetchall()}
    print("Existing columns:", existing)

    for col_name, col_type in NEW_COLUMNS:
        if col_name not in existing:
            sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
            cursor.execute(sql)
            print(f"Added column: {col_name}")
        else:
            print(f"Already exists: {col_name}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
