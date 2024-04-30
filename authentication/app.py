from flask import Flask, request
import psycopg2

app = Flask(__name__)

# Database connection configuration
DATABASE_HOST = "authentication-db"
DATABASE_PORT = 5432
DATABASE_NAME = "authentication_db"
DATABASE_USER = "user"
DATABASE_PASSWORD = "password"

def create_user_table():
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    # Connect to the database
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )
    cursor = conn.cursor()

    # Insert user into database
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return {"success": True}
    except psycopg2.errors.UniqueViolation:
        return {"success": False, "error": "Username already exists"}
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    # Connect to the database
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )
    cursor = conn.cursor()

    # Check if username and password match
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"success": True}
    else:
        return {"success": False, "error": "Invalid username or password"}

if __name__ == "__main__":
    create_user_table()
    app.run(host="0.0.0.0", port=5001)
