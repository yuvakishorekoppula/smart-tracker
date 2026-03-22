import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'student_expenses'

def update_db():
    print("Connecting to MySQL server...")
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()

        print("Checking if 'profile_picture' column exists in 'users' table...")
        cursor.execute("SHOW COLUMNS FROM users LIKE 'profile_picture'")
        result = cursor.fetchone()
        if not result:
            print("Adding 'profile_picture' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) DEFAULT 'default_avatar.png'")
        else:
            print("'profile_picture' column already exists.")

        print("Creating table 'activity_log'...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            action VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        connection.commit()
        print("Database updated successfully!")

    except pymysql.MySQLError as e:
        print(f"Error executing database update: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    update_db()
