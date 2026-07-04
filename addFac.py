import sqlite3
import getpass
from werkzeug.security import generate_password_hash

DATABASE = "database/users.db"

username = input("Username: ").strip().lower()
if not username:
    print("Username cannot be empty.")
    exit()

password = getpass.getpass("Password: ")
if not password:
    print("Password cannot be empty.")
    exit()

print("Select role:")
print("[A] Admin")
print("[F] Faculty")
role = input("Choice: ").strip().lower()

if role == "a":
    role = "admin"
elif role == "f":
    role = "faculty"
else:
    print("Invalid role.")
    exit()

password_hash = generate_password_hash(password)

try:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role)
    )

    conn.commit()
    conn.close()

    print(f"\nUser '{username}' added successfully!")

except sqlite3.IntegrityError:
    print("\nUsername already exists.")
except sqlite3.Error as e:
    print(f"\nDatabase error: {e}")
