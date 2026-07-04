import os
import sqlite3

os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/users.db")
conn2 = sqlite3.connect("database/submissions.db")
cursor = conn.cursor()
cursor2 = conn2.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'faculty'))
)
""")

cursor2.execute("""
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    faculty TEXT NOT NULL,
    program_name TEXT NOT NULL,
    program_type TEXT NOT NULL,
    organizer TEXT NOT NULL,
    venue TEXT,
    start_date TEXT,
    end_date TEXT,
    timestamp TEXT NOT NULL,
    drive_link TEXT NOT NULL
)
""")

conn.commit()
conn2.commit()
conn.close()
conn2.close()


print("Databases created successfully!")
