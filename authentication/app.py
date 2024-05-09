import time

from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection configuration
DATABASE_HOST = "authentication-db"
DATABASE_PORT = 5432
DATABASE_NAME = "authentication-db"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"

# Wait for database to be started
conn = None
while not conn:
    try:
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
    except:
        time.sleep(5)

cursor = conn.cursor()


def create_user_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()


@app.route("/register", methods=["POST"])
def register():
    username = request.json["username"]
    password = request.json["password"]

    # Insert user into database
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return jsonify({"message": "Registration successful"}), 200
    except:
        conn.rollback()
        return jsonify({"message": "Username already exists"}), 400


@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]

    # Check if username and password combination exist
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        return jsonify({"message": "Login succesful"}), 200
    else:
        conn.rollback()
        return jsonify({"message": "Invalid username or password"}), 400


if __name__ == "__main__":
    create_user_table()
    app.run(host="0.0.0.0", port=5001)
    conn.close()
