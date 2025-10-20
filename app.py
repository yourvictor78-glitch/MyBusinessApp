# app.py (FULL REPLACEMENT)

# --- Zarori Libraries Import Karna ---
import os
import psycopg2 # Ab PostgreSQL use karen ge
from psycopg2.extras import RealDictCursor # Data ko dictionary ki tarah access karny ke liye
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash 

# Local testing ke liye (Aap isko delete kar sakte hain agar aapko local test nahi karna)
from dotenv import load_dotenv
load_dotenv() 

# --- Function: Time Ago Filter (Corrected) ---
def format_time_ago(timestamp_str):
    """Timestamp string ko human-readable 'time ago' format mein badalta hai."""
    try:
        # PostgreSQL timestamp ko handle karny ke liye
        if isinstance(timestamp_str, str):
            message_time = datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        elif isinstance(timestamp_str, datetime):
            message_time = timestamp_str
        else:
             return "Unknown Time"
    except ValueError:
        return str(timestamp_str)

    now = datetime.now()
    time_difference = now - message_time

    total_minutes = int(time_difference.total_seconds() / 60)

    if total_minutes < 1:
        if time_difference.total_seconds() < 30:
            return "Just now"
        else:
             return "Less than a minute ago"
    elif total_minutes < 60:
        return f"{total_minutes} minutes ago"
    elif time_difference < timedelta(days=1):
        hours = int(time_difference.total_seconds() / 3600)
        time_part = message_time.strftime('%I:%M %p')
        return f"{hours} hours ago at {time_part}"
    elif time_difference < timedelta(days=7):
        days = time_difference.days
        time_part = message_time.strftime('%I:%M %p')
        if days == 1:
            return f"Yesterday at {time_part}"
        else:
            return f"{days} days ago"
    else:
        return message_time.strftime('%d %b, %Y')


# --- Flask App Shuru Karna ---
app = Flask(__name__)
app.jinja_env.filters['timeago'] = format_time_ago
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-local-use')

# Database URL Environment Variable se len ge
DATABASE_URL = os.environ.get('DATABASE_URL') 
if not DATABASE_URL:
    print("FATAL ERROR: DATABASE_URL environment variable is not set!")
    
# --- Database se Connect Karny ka Helper Function ---
def get_db_connection():
    # Cursor factory ko RealDictCursor set karen taake data dictionary ki tarah mile
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# --- 1. Home Page ---
@app.route('/')
def home():
    return render_template('home.html')

# --- 2. Admin Login Page ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # PostgreSQL mein '?' ke bajaye '%s' use hota hai
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Admin login kamyab ho gaya!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username ya password.', 'error')
    return render_template('login.html')

# --- 3. Admin Panel (Task Add karna) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        flash('Admin access ke liye pehle login karen.', 'error')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        keyword = request.form['keyword']
        assigned_to = request.form['assigned_to']
        
        # PostgreSQL mein CURRENT_DATE ya now() use hota hai
        cur.execute('INSERT INTO tasks (keyword, assigned_to, task_date, due_date) VALUES (%s, %s, now()::date, (now() + interval \'10 days\')::date)',
                     (keyword, assigned_to))
        conn.commit()
        flash('Naya task kamyabi se add ho gaya!', 'success')
        
    cur.execute('SELECT * FROM tasks ORDER BY task_date DESC')
    tasks = cur.fetchall()
    conn.close()
    
    return render_template('admin.html', tasks=tasks)

# --- 4. Team Task Sheet ---
@app.route('/tasks')
def task_list():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Status check karen
    cur.execute('SELECT * FROM tasks WHERE status = %s ORDER BY due_date ASC', ('Pending',))
    pending_tasks = cur.fetchall()
    conn.close()
    
    return render_template('tasks.html', tasks=pending_tasks)

# --- 5. Task Complete karna (Link/Proof save hoga) ---
@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    completion_link = request.form.get('completion_link')
    
    conn = get_db_connection()
    cur = conn.cursor()
    # Task ko complete mark karen aur link ko save karen
    cur.execute('UPDATE tasks SET status = %s, completion_link = %s WHERE id = %s', 
                 ('Completed', completion_link, task_id))
    conn.commit()
    conn.close()
    
    flash('Task complete ho gaya aur proof link save ho gaya. Shabash!', 'success')
    return redirect(url_for('task_list'))

# --- 6. Messenger Page ---
@app.route('/messenger', methods=['GET', 'POST'])
def messenger():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        sender_name = request.form['sender_name']
        message_body = request.form['message_body']
        
        if sender_name and message_body:
            # Timestamp automatic save ho jaye ga
            cur.execute('INSERT INTO messages (sender_name, message_body) VALUES (%s, %s)',
                         (sender_name, message_body))
            conn.commit()
            conn.close()
            return redirect(url_for('messenger'))

    cur.execute('SELECT * FROM messages ORDER BY timestamp ASC')
    messages = cur.fetchall()
    conn.close()
    
    return render_template('messenger.html', messages=messages)

# --- 7. Logout Function ---
@app.route('/logout')
def logout():
    session.clear()
    flash('Aap logout ho gaye hain.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Local test ke liye, pehle aapko DATABASE_URL environment variable set karna hoga
    app.run(debug=True)