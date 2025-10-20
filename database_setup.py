# database_setup.py (FULL REPLACEMENT - SQLite Version)

import sqlite3
from werkzeug.security import generate_password_hash
import sys

# --- Database file ka naam ---
DATABASE_NAME = 'app_database.db'

print(f"SQLite database setup script shuru ho raha hai ({DATABASE_NAME})...")

try:
    # Database se connect karen
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 1. 'users' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    ''')
    print("Users table check/create ho gaya.")

    # 2. 'tasks' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        keyword TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        task_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        completion_link TEXT
    );
    ''')
    print("Tasks table check/create ho gaya.")

    # 3. 'messages' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        sender_name TEXT NOT NULL,
        message_body TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    ''')
    print("Messages table check/create ho gaya.")


    # --- Admin User Add Karna ---
    admin_username = 'admin'
    admin_password = 'your_secret_password_123' # <-- YAHAN APNA PASSWORD RAKHEN

    cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
    admin_user_exists = cursor.fetchone()

    if admin_user_exists is None:
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (admin_username, hashed_password))
        print(f"Admin user '{admin_username}' banaya gaya hai. Password: {admin_password}")
    else:
        print("Admin user pehle se maujood hai. Skipped.")


    # Changes ko save karen
    conn.commit()
    conn.close()
    print("Database setup complete.")

except sqlite3.Error as e:
    print(f"\nFATAL: Database error aa gaya: {e}")
    sys.exit(1)