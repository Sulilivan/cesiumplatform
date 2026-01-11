import sqlite3
import os

def add_column():
    db_path = 'water_platform.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE monitor_points ADD COLUMN bind_model_id VARCHAR")
        conn.commit()
        print("Column 'bind_model_id' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Operation info: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()