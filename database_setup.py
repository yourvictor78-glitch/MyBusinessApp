# database_setup.py (FULL REPLACEMENT - PostgreSQL)

import os
import sys
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Local testing ke liye environment variables load karen
load_dotenv() 

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable set nahi hai.")
    print("Database URL set kiye bagair yeh script nahi chal sakta.")
    sys.exit(1)

print("PostgreSQL database setup script shuru ho raha hai...")

try:
    # Database se connect karen
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # 1. 'users' table (PostgreSQL syntax)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    );
    ''')
    print("Users table check/create ho gaya.")

    # 2. 'tasks' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        keyword VARCHAR(255) NOT NULL,
        assigned_to VARCHAR(80) NOT NULL,
        task_date DATE NOT NULL,
        due_date DATE NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'Pending',
        completion_link TEXT
    );
    ''')
    print("Tasks table check/create ho gaya.")

    # 3. 'messages' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        sender_name VARCHAR(80) NOT NULL,
        message_body TEXT NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Messages table check/create ho gaya.")


    # --- Admin User Add Karna ---
    admin_username = 'admin'
    admin_password = 'your_secret_password_123' # <-- YAHAN APNA PASSWORD LIKHEN

    cursor.execute("SELECT id FROM users WHERE username = %s", (admin_username,))
    admin_user_exists = cursor.fetchone()

    if admin_user_exists is None:
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", 
                       (admin_username, hashed_password))
        print(f"Admin user '{admin_username}' banaya gaya hai. Password: {admin_password}")
    else:
        print("Admin user pehle se maujood hai. Skipped.")


    # Changes ko save karen
    conn.commit()
    conn.close()
    print("Database setup complete.")

except psycopg2.Error as e:
    print(f"\nFATAL: Database connection ya SQL error aa gaya: {e}")
    sys.exit(1)