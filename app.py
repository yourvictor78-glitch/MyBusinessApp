# app.py (FULL REPLACEMENT - SQLite Version)

import os
import sqlite3 # Wapas SQLite use karen ge
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash 

# --- Database file ka naam aur path set karen ---
# PythonAnywhere mein file system thoda alag hota hai, isliye sirf naam istemal karen ge.
DATABASE_NAME = 'app_database.db'

# --- Function: Time Ago Filter (Corrected) ---
def format_time_ago(timestamp_str):
    """Timestamp string ko human-readable 'time ago' format mein badalta hai."""
    try:
        # SQLite aur general timestamp ko handle karny ke liye
        if isinstance(timestamp_str, str):
            # Split karna zaroori hai agar microsecond bhi ho
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
app.config['SECRET_KEY'] = 'ye-koi-secret-key-yahan-dalen' # Secret Key seedha yahan set karen

# --- Database se Connect Karny ka Helper Function ---
def get_db_connection():
    # Row Factory se data dictionary ki tarah milega
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row 
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
        cur = conn.cursor()
        # SQLite mein '?' use hota hai
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
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
    cur = conn.cursor()
    
    if request.method == 'POST':
        keyword = request.form['keyword']
        assigned_to = request.form['assigned_to']
        
        # SQLite mein datetime('now') use hota hai
        cur.execute('INSERT INTO tasks (keyword, assigned_to, task_date, due_date) VALUES (?, ?, date(\'now\'), date(\'now\', \'+10 days\'))',
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
    cur = conn.cursor()
    # Status check karen
    cur.execute('SELECT * FROM tasks WHERE status = ? ORDER BY due_date ASC', ('Pending',))
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
    cur.execute('UPDATE tasks SET status = ?, completion_link = ? WHERE id = ?', 
                 ('Completed', completion_link, task_id))
    conn.commit()
    conn.close()
    
    flash('Task complete ho gaya aur proof link save ho gaya. Shabash!', 'success')
    return redirect(url_for('task_list'))

# --- 6. Messenger Page ---
@app.route('/messenger', methods=['GET', 'POST'])
def messenger():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        sender_name = request.form['sender_name']
        message_body = request.form['message_body']
        
        if sender_name and message_body:
            # Timestamp automatic save ho jaye ga
            cur.execute('INSERT INTO messages (sender_name, message_body, timestamp) VALUES (?, ?, datetime(\'now\'))',
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
    # Local test ke liye
    app.run(debug=True)