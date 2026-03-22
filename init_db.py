import os
import pymysql

def init_db():
    print("Connecting to MySQL server...")
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='', # Default xampp/wamp or typical local setup
        )
        cursor = connection.cursor()

        print("Creating database 'student_expenses' if it does not exist...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_expenses")
        cursor.execute("USE student_expenses")

        print("Creating table 'users'...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone VARCHAR(15) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            budget_limit DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        print("Creating table 'expenses'...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        connection.commit()
        print("Database initialized successfully!")

    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL Platform: {e}")
        print("Please ensure MySQL server is running locally with user 'root' and no password on port 3306.")
        
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    init_db()
