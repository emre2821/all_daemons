import sqlite3
from datetime import datetime

DB_PATH = "chaos_index.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chaos_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT,
            converted_name TEXT,
            agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tags TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_to_db(original, converted, agent="Unknown", tags=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO chaos_files (original_name, converted_name, agent, tags)
        VALUES (?, ?, ?, ?)
    ''', (original, converted, agent, tags))
    conn.commit()
    conn.close()
