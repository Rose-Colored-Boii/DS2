import time

from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection configuration
DATABASE_HOST = "calendar-db"
DATABASE_PORT = 5432
DATABASE_NAME = "calendar-db"
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


def create_calendar_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendars (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            event_id INT NOT NULL
        )
    """)
    conn.commit()


def create_invites_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invites (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            invitee VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()


@app.route("/calendar/<username>/invites", methods=["POST"])
def invite(username):
    try:
        invitee = request.json["invitee"]
        cursor.execute("INSERT INTO invites (username, invitee) VALUES (%s, %s)", (username, invitee))
        conn.commit()
        return jsonify({"message": "Succesfully sent invite"}), 200
    except:
        conn.rollback()
        return jsonify({"message": "Error occured sending invite"}), 400


@app.route("/calendar/<username>/invites", methods=["GET"])
def get_invitees(username):
    try:
        cursor.execute("SELECT * FROM invites WHERE username = %s", (username, ))
        invites = cursor.fetchall()
        json = {"invitees": []}
        for invite in invites:
            json["invitees"].append(invite[2])
        return jsonify(json), 200
    except:
        conn.rollback()
        return jsonify({"message": "Error occured fetching invites"}), 400


@app.route("/calendar/<username>", methods=["GET"])
def get_calendar(username):
    try:
        cursor.execute("SELECT * FROM calendars WHERE username = %s", (username, ))
        calendar = cursor.fetchall()
        json = {"event_ids": []}
        for event_id in calendar:
            json["event_ids"].append(event_id[2])
        return jsonify(json), 200
    except:
        conn.rollback()
        return jsonify({"message": "Error occured fetching calendar"}), 400


@app.route("/calendar/<username>", methods=["POST"])
def add_event(username):
    try:
        event_id = request.json["event_id"]
        cursor.execute("INSERT INTO calendars (username, event_id) VALUES (%s, %s)", (username, event_id))
        conn.commit()
        return jsonify({"message": "Added event to calendar"}), 200
    except:
        conn.rollback()
        return jsonify({"message": "Error occured adding event to calendar"}), 400


if __name__ == "__main__":
    create_calendar_table()
    create_invites_table()
    app.run(host="0.0.0.0", port=5003)
    conn.close()
