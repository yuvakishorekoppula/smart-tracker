import os
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'student_expenses'

def generate_data():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        print(f"Error connecting to database: {e}")
        return

    try:
        with connection.cursor() as cursor:
            # Create a demo user
            print("Creating demo user...")
            demo_phone = "1234567890"
            demo_password = "password123"
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE phone = %s", (demo_phone,))
            user = cursor.fetchone()
            
            if user:
                user_id = user['id']
                print(f"Demo user already exists with ID: {user_id}")
                # Clear existing expenses for a clean slate
                cursor.execute("DELETE FROM expenses WHERE user_id = %s", (user_id,))
            else:
                hashed_password = generate_password_hash(demo_password)
                cursor.execute(
                    "INSERT INTO users (name, email, phone, password_hash, budget_limit) VALUES (%s, %s, %s, %s, %s)",
                    ("Demo Student", "demo@student.edu", demo_phone, hashed_password, 15000.00)
                )
                user_id = cursor.lastrowid
                print(f"Created demo user with ID: {user_id}")

            # Generate sample expenses
            print("Generating sample expenses...")
            categories = ['Food', 'Travel', 'Books', 'Entertainment', 'Shopping', 'Other']
            descriptions = {
                'Food': ['Cafeteria lunch', 'Coffee with friends', 'Groceries', 'Dinner out', 'Snacks'],
                'Travel': ['Bus pass', 'Uber to mall', 'Train ticket home', 'Gas'],
                'Books': ['Textbook for CS101', 'Notebooks and pens', 'Online course subscription'],
                'Entertainment': ['Movie ticket', 'Spotify subscription', 'Concert ticket'],
                'Shopping': ['New shirt', 'Shoes', 'Electronics accessory'],
                'Other': ['Pharmacy', 'Gym membership', 'Haircut']
            }
            
            # Generate 50 expenses over the last 6 months
            today = datetime.now()
            for _ in range(50):
                # Random date within last 180 days
                days_ago = random.randint(0, 180)
                exp_date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                category = random.choice(categories)
                description = random.choice(descriptions[category])
                
                # Assign amount based on category to make it somewhat realistic
                if category == 'Books':
                    amount = round(random.uniform(500, 2500), 2)
                elif category == 'Food':
                    amount = round(random.uniform(100, 800), 2)
                elif category == 'Travel':
                    amount = round(random.uniform(50, 400), 2)
                else:
                    amount = round(random.uniform(200, 1500), 2)

                cursor.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, amount, category, exp_date, description)
                )

            connection.commit()
            print("Successfully inserted 50 sample expenses! Charts and Reports should now be populated.")
            print(f"--- DEMO LOGIN CREADENTIALS ---")
            print(f"Phone: {demo_phone}")
            print(f"Password: {demo_password}")
            print(f"-------------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    generate_data()
