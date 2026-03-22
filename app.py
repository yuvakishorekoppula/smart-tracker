from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime, timedelta
import os
import time
import random
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = 'super_secret_session_key' # In production, use os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'profiles')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# DB Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'student_expenses'

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to database: {e}")
        return None

# Utility: Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- UTILITY FUNCTIONS -----------------
def log_activity(user_id, action):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO activity_log (user_id, action) VALUES (%s, %s)", (user_id, action))
                conn.commit()
        except Exception as e:
            print(f"Activity Log Error: {e}")
        finally:
            conn.close()

def send_hybrid_otp(target_phone):
    """Generates a 6-digit OTP and attempts to send it via Twilio. Falls back to mock on failure."""
    otp_code = "{:06d}".format(random.randint(0, 999999))
    
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not (twilio_sid and twilio_token and twilio_phone):
        print(f"Twilio credentials missing. Falling back to Mock OTP. Target: {target_phone}")
        return '123456', True
        
    try:
        client = Client(twilio_sid, twilio_token)
        message = client.messages.create(
            body=f"Your SmartExp verification code is: {otp_code}. Valid for 5 minutes.",
            from_=twilio_phone,
            to=target_phone
        )
        print(f"Twilio message sent successfully: SID {message.sid}")
        return otp_code, False
    except Exception as e:
        print(f"Twilio Error: {e}. Falling back to Mock OTP. Target: {target_phone}")
        return '123456', True

@app.context_processor
def inject_user():
    user_data = {'name': 'Student', 'profile_picture': 'default_avatar.png'}
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT name, email, phone, profile_picture FROM users WHERE id = %s", (session['user_id'],))
                    user = cursor.fetchone()
                    if user:
                        user_data = user
            finally:
                conn.close()
    return dict(current_user=user_data)


# ----------------- ROUTES -----------------

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    if not conn:
        return "Database error"
        
    insights = []
    
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            
            # Fetch user budget limit
            cursor.execute("SELECT budget_limit FROM users WHERE id = %s", (user_id,))
            user_row = cursor.fetchone()
            budget_limit = float(user_row['budget_limit']) if user_row and user_row['budget_limit'] else 0.00
            
            # Total expenses today
            current_date_str = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s AND DATE(date) = %s", (user_id, current_date_str))
            total_today = float(cursor.fetchone()['total'] or 0.00)

            # Total expenses this month
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s AND DATE_FORMAT(date, '%%Y-%%m') = %s", (user_id, current_month))
            total_month = float(cursor.fetchone()['total'] or 0.00)
            
            # Total expenses all time
            cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s", (user_id,))
            total_all = float(cursor.fetchone()['total'] or 0.00)
            
            # Total transactions count
            cursor.execute("SELECT COUNT(id) as count FROM expenses WHERE user_id = %s", (user_id,))
            total_transactions = cursor.fetchone()['count'] or 0
            
            # Recent expenses
            cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC LIMIT 5", (user_id,))
            recent_expenses = cursor.fetchall()
            
            # Top category this month
            cursor.execute("""
                SELECT category, SUM(amount) as cat_total
                FROM expenses
                WHERE user_id = %s AND DATE_FORMAT(date, '%%Y-%%m') = %s
                GROUP BY category
                ORDER BY cat_total DESC
                LIMIT 1
            """, (user_id, current_month))
            top_cat = cursor.fetchone()
            
            # Generate Insights
            if top_cat:
                insights.append({
                    'type': 'info',
                    'icon': 'fa-lightbulb',
                    'message': f"You spent the most on {top_cat['category']} this month (₹{top_cat['cat_total']:.2f})."
                })
                
            if budget_limit > 0:
                if total_month > budget_limit:
                    insights.append({
                        'type': 'warning',
                        'icon': 'fa-triangle-exclamation',
                        'message': f"You have exceeded your monthly budget of ₹{budget_limit:.2f} by ₹{(total_month - budget_limit):.2f}!"
                    })
                elif total_month > (budget_limit * 0.8):
                    insights.append({
                        'type': 'warning',
                        'icon': 'fa-bell',
                        'message': f"You have used {(total_month / budget_limit) * 100:.1f}% of your monthly budget. Watch out!"
                    })
    finally:
        conn.close()
        
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('dashboard.html', 
                           total_today=total_today,
                           total_expenses_month=total_month,
                           total_expenses_all=total_all,
                           total_transactions=total_transactions,
                           recent_expenses=recent_expenses,
                           insights=insights,
                           current_date=current_date)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return render_template('auth.html', view='login')

        try:
            with conn.cursor() as cursor:
                # Allow login by name or phone
                cursor.execute("SELECT * FROM users WHERE name = %s OR phone = %s", (identifier, identifier))
                user = cursor.fetchone()
                
                if not user:
                    flash("User not registered.", "danger")
                elif check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    log_activity(user['id'], "Logged in successfully")
                    return redirect(url_for('index'))
                else:
                    flash("Invalid password.", "danger")
        finally:
            conn.close()
            
    return render_template('auth.html', view='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return render_template('auth.html', view='register')
            
        try:
            with conn.cursor() as cursor:
                # Check if phone, email, or name already exists
                cursor.execute("SELECT id FROM users WHERE phone = %s OR email = %s OR name = %s", (phone, email, name))
                if cursor.fetchone():
                    flash("Account with this name, phone number, or email already exists.", "danger")
                    return render_template('auth.html', view='register')
                
                # Insert new user
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (name, email, phone, password_hash) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, hashed_password)
                )
                conn.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for('login'))
        finally:
            conn.close()
            
    return render_template('auth.html', view='register')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], "Logged out")
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        if not identifier:
            flash("Please enter a valid name or phone number.", "warning")
            return redirect(url_for('forgot_password'))
            
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return render_template('auth.html', view='forgot-password')
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, phone FROM users WHERE name = %s OR phone = %s", (identifier, identifier))
                user = cursor.fetchone()
                
                if user:
                    otp_code, is_mock = send_hybrid_otp(user['phone'])
                    
                    session['reset_user_id'] = user['id']
                    session['reset_identifier'] = identifier
                    session['reset_otp'] = otp_code
                    session['otp_expiry'] = time.time() + 300 # 5 minutes from now
                    
                    if is_mock:
                        flash(f"A demo OTP has been sent. (Use: {otp_code})", "info")
                    else:
                        flash(f"An OTP has been sent to {user['phone']} via SMS.", "success")
                        
                    return redirect(url_for('verify_otp'))
                else:
                    flash("User not found.", "danger")
        finally:
            conn.close()
            
    return render_template('auth.html', view='forgot-password')

@app.route('/resend-otp')
def resend_otp():
    if 'reset_identifier' not in session or 'reset_user_id' not in session:
        return redirect(url_for('forgot_password'))
        
    user_id = session['reset_user_id']
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('verify_otp'))
        
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT phone FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                otp_code, is_mock = send_hybrid_otp(user['phone'])
                session['reset_otp'] = otp_code
                session['otp_expiry'] = time.time() + 300
                
                if is_mock:
                    flash(f"A demo OTP has been sent. (Use: {otp_code})", "info")
                else:
                    flash(f"A new OTP has been sent to {user['phone']} via SMS.", "success")
    finally:
        conn.close()
        
    return redirect(url_for('verify_otp'))

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_identifier' not in session:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        user_otp = request.form.get('otp')
        
        # Check expiry
        if 'otp_expiry' in session and time.time() > session['otp_expiry']:
            flash("OTP has expired. Please request a new one.", "warning")
            return redirect(url_for('verify_otp'))
            
        if user_otp == session.get('reset_otp'):
            flash("OTP verified. Please set a new password.", "success")
            # Clear OTP from session to prevent reuse, but keep identifier for reset
            session.pop('reset_otp', None)
            session['otp_verified'] = True
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Try again.", "danger")
    return render_template('auth.html', view='verify-otp')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified') or 'reset_user_id' not in session:
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth.html', view='reset-password')
            
        user_id = session.get('reset_user_id')
        hashed_password = generate_password_hash(new_password)
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, user_id))
                    conn.commit()
            finally:
                conn.close()
                
            session.pop('reset_identifier', None)
            session.pop('reset_user_id', None)
            session.pop('otp_expiry', None)
            session.pop('otp_verified', None)
            flash("Password updated successfully. Please log in.", "success")
            return redirect(url_for('login'))
            
    return render_template('auth.html', view='reset-password')

@app.route('/expenses')
@login_required
def expenses():
    category_filter = request.args.get('category')
    user_id = session['user_id']
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('index'))
        
    try:
        with conn.cursor() as cursor:
            if category_filter:
                cursor.execute("SELECT * FROM expenses WHERE user_id = %s AND category = %s ORDER BY date DESC, id DESC", (user_id, category_filter))
            else:
                cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC", (user_id,))
            user_expenses = cursor.fetchall()
    finally:
        conn.close()
        
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('expenses.html', expenses=user_expenses, current_date=current_date)

@app.route('/add-expense', methods=['POST'])
@login_required
def add_expense():
    amount = request.form.get('amount')
    category = request.form.get('category')
    date = request.form.get('date')
    description = request.form.get('description')
    user_id = session['user_id']
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, amount, category, date, description)
                )
                conn.commit()
                log_activity(user_id, f"Added expense: {category} (₹{amount})")
                flash("Expense added successfully!", "success")
        finally:
            conn.close()
    
    return redirect(request.referrer or url_for('expenses'))

@app.route('/delete-expense/<int:id>')
@login_required
def delete_expense(id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (id, user_id))
                conn.commit()
                log_activity(user_id, "Deleted an expense record")
                flash("Expense deleted.", "info")
        finally:
            conn.close()
    
    return redirect(request.referrer or url_for('expenses'))

@app.route('/reports')
@login_required
def reports():
    user_id = session['user_id']
    conn = get_db_connection()
    monthly_summary = []
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # Basic monthly summary calculation
                cursor.execute("""
                    SELECT DATE_FORMAT(date, '%%Y-%%m') as month, SUM(amount) as total
                    FROM expenses 
                    WHERE user_id = %s 
                    GROUP BY DATE_FORMAT(date, '%%Y-%%m')
                    ORDER BY month DESC
                """, (user_id,))
                
                rows = cursor.fetchall()
                for row in rows:
                    month_str = row['month']
                    # Find top category for this month
                    cursor.execute("""
                        SELECT category, SUM(amount) as cat_total
                        FROM expenses
                        WHERE user_id = %s AND DATE_FORMAT(date, '%%Y-%%m') = %s
                        GROUP BY category
                        ORDER BY cat_total DESC
                        LIMIT 1
                    """, (user_id, month_str))
                    top_cat = cursor.fetchone()
                    
                    monthly_summary.append({
                        'month': month_str,
                        'total': row['total'],
                        'top_category': top_cat['category'] if top_cat else 'N/A'
                    })
        finally:
            conn.close()
            
    return render_template('reports.html', monthly_summary=monthly_summary)

@app.route('/api/chart-data')
@login_required
def chart_data():
    user_id = session['user_id']
    time_filter = request.args.get('filter', 'monthly')
    conn = get_db_connection()
    
    data = {
        'pie_labels': [],
        'pie_values': [],
        'bar_labels': [],
        'bar_values': []
    }
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # Category breakdown based on filter time range
                if time_filter == 'daily':
                    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY category", (user_id,))
                elif time_filter == 'weekly':
                    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 28 DAY) GROUP BY category", (user_id,))
                else: # monthly or default
                    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) GROUP BY category", (user_id,))
                    
                categories = cursor.fetchall()
                for c in categories:
                    data['pie_labels'].append(c['category'])
                    data['pie_values'].append(float(c['total']))
                
                # Bar chart trends
                if time_filter == 'daily':
                    cursor.execute("""
                        SELECT DATE_FORMAT(date, '%%Y-%%m-%%d') as label, SUM(amount) as total 
                        FROM expenses 
                        WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                        GROUP BY label 
                        ORDER BY label ASC
                    """, (user_id,))
                elif time_filter == 'weekly':
                    cursor.execute("""
                        SELECT CONCAT(YEAR(date), '-W', WEEK(date)) as label, SUM(amount) as total 
                        FROM expenses 
                        WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 28 DAY)
                        GROUP BY label 
                        ORDER BY label ASC
                    """, (user_id,))
                else: # monthly or default
                    cursor.execute("""
                        SELECT DATE_FORMAT(date, '%%Y-%%m') as label, SUM(amount) as total 
                        FROM expenses 
                        WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                        GROUP BY label 
                        ORDER BY label ASC
                    """, (user_id,))
                    
                periods = cursor.fetchall()
                for p in periods:
                    data['bar_labels'].append(p['label'])
                    data['bar_values'].append(float(p['total']))
        finally:
            conn.close()
            
    return jsonify(data)

import csv
from flask import Response, stream_with_context

@app.route('/export-csv')
@login_required
def export_csv():
    user_id = session['user_id']
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('reports'))
        
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT date, category, description, amount FROM expenses WHERE user_id = %s ORDER BY date DESC", (user_id,))
            expenses = cursor.fetchall()
            
        def generate():
            data = [('Date', 'Category', 'Description', 'Amount')]
            for row in expenses:
                data.append((row['date'].strftime('%Y-%m-%d'), row['category'], row['description'], str(row['amount'])))
                
            for row in data:
                yield ','.join(row) + '\\n'
                
        return Response(stream_with_context(generate()), 
                       mimetype='text/csv', 
                       headers={"Content-Disposition": "attachment; filename=expenses_report.csv"})
    finally:
        conn.close()

# --- PROFILE ROUTES ---

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        try:
            with conn.cursor() as cursor:
                # Check for duplicate phone
                cursor.execute("SELECT id FROM users WHERE phone = %s AND id != %s", (phone, user_id))
                if cursor.fetchone():
                    flash("Phone number is already associated with another account.", "danger")
                else:
                    cursor.execute("UPDATE users SET name = %s, phone = %s WHERE id = %s", (name, phone, user_id))
                    conn.commit()
                    log_activity(user_id, "Updated profile details")
                    flash("Profile updated successfully.", "success")
                    session['user_name'] = name
        finally:
            conn.close()
        return redirect(url_for('profile'))
        
    activity_logs = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT action, created_at FROM activity_log WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (user_id,))
            activity_logs = cursor.fetchall()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_info = cursor.fetchone()
    finally:
        conn.close()
        
    return render_template('profile.html', user=user_info, logs=activity_logs)

@app.route('/profile/password', methods=['POST'])
@login_required
def update_password():
    user_id = session['user_id']
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('profile'))
        
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password_hash'], old_password):
                    hashed = generate_password_hash(new_password)
                    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
                    conn.commit()
                    log_activity(user_id, "Changed account password")
                    flash("Password changed successfully.", "success")
                else:
                    flash("Current password is incorrect.", "danger")
        finally:
            conn.close()
            
    return redirect(url_for('profile'))

@app.route('/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    user_id = session['user_id']
    if 'avatar' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('profile'))
        
    file = request.files['avatar']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('profile'))
        
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        filename = secure_filename(f"user_{user_id}_{int(time.time())}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE users SET profile_picture = %s WHERE id = %s", (filename, user_id))
                    conn.commit()
                    log_activity(user_id, "Updated profile picture")
                    flash("Profile picture updated!", "success")
            finally:
                conn.close()
    else:
        flash("Invalid file format. Allowed: png, jpg, jpeg, gif, webp", "danger")
        
    return redirect(url_for('profile'))

@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user_id = session['user_id']
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
        finally:
            conn.close()
            
    session.clear()
    flash("Your account has been permanently deleted.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
