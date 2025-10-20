import sqlite3
from werkzeug.security import generate_password_hash
import sys

# --- 1. YAHAN APNA NAYA PASSWORD LIKHEN ---
# Is line mein apna naya password likhen jo aap rakhna chahty hain
NEW_PASSWORD = "171209" 

# --- 2. Aap ka Admin Username ---
# Hum ne username 'admin' rakha tha
ADMIN_USERNAME = "admin"


# --- Baqi code ko change karny ki zarorat nahi ---

DATABASE_NAME = 'app_database.db'

if NEW_PASSWORD == "my_new_strong_password_123":
    print("Error: Aap ne code mein 'NEW_PASSWORD' ki value change nahi ki.")
    print("Please file 'update_password.py' ko edit karen aur apna naya password likhen.")
    sys.exit() # Program ko rok den

print(f"'{ADMIN_USERNAME}' ka password update karny ki koshish ki ja rahi hai...")

try:
    # Naye password ka hash (encrypted version) banayen
    hashed_password = generate_password_hash(NEW_PASSWORD)
    
    # Database se connect karen
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Database mein password update karny ki SQL command
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                   (hashed_password, ADMIN_USERNAME))
    
    # Check karen ke password update hua ya nahi
    if cursor.rowcount == 0:
        print(f"Error! '{ADMIN_USERNAME}' naam ka user database mein nahi mila.")
    else:
        # Changes ko save karen
        conn.commit()
        print("--------------------------------------------------")
        print(f"Success! '{ADMIN_USERNAME}' ka password update ho gaya hai.")
        print("--------------------------------------------------")

except sqlite3.Error as e:
    print(f"Database mein error aa gaya: {e}")
except Exception as e:
    print(f"Ek unexpected error aa gaya: {e}")
    print("Kya aap ne 'pip install werkzeug' command chalai thi?")
finally:
    if conn:
        conn.close()
        print("Database connection band ho gaya.")