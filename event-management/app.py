import time

from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection configuration
DATABASE_HOST = "event-management-db"
DATABASE_PORT = 5432
DATABASE_NAME = "event-management-db"
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


def create_event_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            date VARCHAR(255) NOT NULL,
            organizer VARCHAR(255) NOT NULL,
            privacy VARCHAR(255) NOT NULL,
            description VARCHAR(255)
        )
    """)
    conn.commit()

def create_invites_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invites (
            id SERIAL PRIMARY KEY,
            event_id integer REFERENCES events,
            username VARCHAR(255) NOT NULL,
            status VARCHAR (255) NOT NULL
        )
    """)
    conn.commit()


@app.route("/create_event", methods=["POST"])
def create_event():
    try:
        title, description, date, publicprivate, organizer = request.json['title'], request.json['description'], request.json['date'], request.json['publicprivate'], request.json['organizer']
        cursor.execute("INSERT INTO events (title, date, organizer, privacy, description) VALUES (%s, %s, %s, %s, %s)", (title, date, organizer, publicprivate, description))
        return jsonify({"message": "Event created succesfully"}), 200
    except:
        return jsonify({"message": "Error occured during event creation"}), 400


@app.route("/get_events", methods=["GET"])
def get_events():
    try:
        event_id = request.json["event_id"]
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        cursor.execute("SELECT * FROM invites WHERE event_id = %s", (event_id,))
        invites = cursor.fetchall()
        json = {"event": {"title": event[1], "date": event[2], "organizer": event[3], "privacy": event[4]}, "invites": []}
        for invite in invites:
            json["invites"].append({"username": invite[2], "status": invite[3]})
        return jsonify(json), 200
    except:
        return jsonify({"message": "Error occured fetching events"}), 400

@app.route("/get_public_events", methods=["GET"])
def get_public_events():
    try:
        cursor.execute("SELECT * FROM events WHERE privacy = 'public'")
        events = cursor.fetchall()
        json = {"events": []}
        for event in events:
            json["events"].append({"title": event[1], "date": event[2], "organizer": event[3]})
        return jsonify(json), 200
    except:
        return jsonify({"message": "Error occured fetching public events"}), 400


@app.route("/invite", methods=["POST"])
def invite():
    try:
        names, organizer, title = request.json["invites"], request.json["organizer"], request.json["title"]
        cursor.execute("SELECT * FROM events WHERE organizer = %s AND title = %s", (organizer, title))
        event_id = cursor.fetchone()[0]
        for username in names:
            cursor.execute("INSERT INTO invites (event_id, username, status) VALUES (%s, %s, 'TBD')", (event_id, username,))
        return jsonify({"message": "Invites sent out correctly"}), 200
    except:
        return jsonify({"message": "Error while sending out invites"}), 400


@app.route("/get_invites", methods=["GET"])
def get_invites():
    try:
        username = request.json["username"]
        cursor.execute("SELECT * FROM invites WHERE username = %s AND status = 'TBD'", (username,))
        invites = cursor.fetchall()
        response = {"invites": []}
        for invite in invites:
            event_id = invite[1]
            cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
            event = cursor.fetchone()
            response["invites"].append({"id": event_id, "title": event[1], "date": event[2], "organizer": event[3], "privacy": event[4]})
        return jsonify(response), 200
    except:
        return jsonify({"message": "Error while fetching invites"}), 400

@app.route("/update_invites", methods=["POST"])
def update_invites():
    try:
        username, event_id, status = request.json["username"], request.json["event_id"], request.json["status"]
        cursor.execute("UPDATE invites SET status = %s WHERE username = %s AND event_id = %s", (status, username, event_id))
        return jsonify({"message": "Invites updated correctly"}), 200
    except:
        return jsonify({"message": "Error while updating invites"}), 400

if __name__ == "__main__":
    create_event_table()
    create_invites_table()
    app.run(host="0.0.0.0", port=5002)
    conn.close()
