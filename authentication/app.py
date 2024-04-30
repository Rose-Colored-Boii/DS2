import time

from flask import Flask, request
import psycopg2

app = Flask(__name__)

# Wait for database to be started
time.sleep(5)

# Database connection configuration
DATABASE_HOST = "authentication-db"
DATABASE_PORT = 5432
DATABASE_NAME = "authentication-db"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"


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
            username VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
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
        conn.close()
        return {"success": True}, 200
    except:
        conn.close()
        return {"success": False}, 400


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

    # Check if username and password combination exist
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"success": True}, 200
    else:
        return {"success": False}, 400


if __name__ == "__main__":
    create_user_table()
    app.run(host="0.0.0.0", port=5001)
