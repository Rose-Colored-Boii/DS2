from flask import Flask, render_template, redirect, request, url_for
import requests

app = Flask(__name__)

AUTH_SERVICE_URL = "http://ds2-authentication-1:5001"
EVENT_SERVICE_URL = "http://ds2-event-management-1:5002"
CALENDAR_SERVICE_URL = "http://ds2-calendar-1:5003"

# The Username & Password of the currently logged-in User, this is used as a pseudo-cookie, as such this is not session-specific.
username = None
password = None

session_data = dict()


def save_to_session(key, value):
    session_data[key] = value


def load_from_session(key):
    return session_data.pop(key) if key in session_data else None  # Pop to ensure that it is only used once


def succesful_request(r):
    return r.status_code == 200


@app.route("/")
def home():
    global username

    if username is None:
        return render_template('login.html', username=username, password=password)
    else:
        # ================================
        # FEATURE (list of public events)
        #
        # Retrieve the list of all public events. The webpage expects a list of (title, date, organizer) tuples.
        # Try to keep in mind failure of the underlying microservice
        # =================================
        public_events = []
        events = requests.get(f"{EVENT_SERVICE_URL}/get_public_events").json()["events"]
        for event in events:
            public_events.append((event["title"], event["date"], event["organizer"]))
        return render_template('home.html', username=username, password=password, events=public_events)


@app.route("/event", methods=['POST'])
def create_event():
    title, description, date, publicprivate, invites = request.form['title'], request.form['description'], request.form['date'], request.form['publicprivate'], request.form['invites']
    #==========================
    # FEATURE (create an event)
    #
    # Given some data, create an event and send out the invites.
    #==========================

    requests.post(f"{EVENT_SERVICE_URL}/create_event", json={"title": title, "description": description, "date": date, "publicprivate": publicprivate, "organizer": username})
    requests.post(f"{EVENT_SERVICE_URL}/invite", json={"title": title, "organizer": username, "invites": invites.split(';')})

    return redirect('/')


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    calendar_user = request.form['calendar_user'] if 'calendar_user' in request.form else username

    # ================================
    # FEATURE (calendar based on username)
    #
    # Retrieve the calendar of a certain user. The webpage expects a list of (id, title, date, organizer, status, Public/Private) tuples.
    # Try to keep in mind failure of the underlying microservice
    # =================================

    success = True # TODO: this might change depending on if the calendar is shared with you

    if success:
        calendar = [(1, 'Test event', 'Tomorrow', 'Benjamin', 'Going', 'Public')]  # TODO: call
    else:
        calendar = None


    return render_template('calendar.html', username=username, password=password, calendar_user=calendar_user, calendar=calendar, success=success)

@app.route('/share', methods=['GET'])
def share_page():
    return render_template('share.html', username=username, password=password, success=None)

@app.route('/share', methods=['POST'])
def share():
    share_user = request.form['username']

    #========================================
    # FEATURE (share a calendar with a user)
    #
    # Share your calendar with a certain user. Return success = true / false depending on whether the sharing is succesful.
    #========================================

    success = True  # TODO
    return render_template('share.html', username=username, password=password, success=success)


@app.route('/event/<eventid>')
def view_event(eventid):

    # ================================
    # FEATURE (event details)
    #
    # Retrieve additional information for a certain event parameterized by an id. The webpage expects a (title, date, organizer, status, (invitee, participating)) tuples.
    # Try to keep in mind failure of the underlying microservice
    # =================================

    response = requests.get(f"{EVENT_SERVICE_URL}/get_events", json={"event_id": eventid}).json()

    event = [response["event"]["title"], response["event"]["date"], response["event"]["organizer"], response["event"]["privacy"], []]

    success = False

    if event[3] == "public" or event[2] == username:
        success = True

    for invite in response["invites"]:
        if invite["username"] == username:
            success = True
        event[4].append([invite["username"], invite["status"]])

    if not success:
        event = None

    return render_template('event.html', username=username, password=password, event=event, success=success)

@app.route("/login", methods=['POST'])
def login():
    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    response = requests.post(f"{AUTH_SERVICE_URL}/login", json={"username": req_username, "password": req_password})

    success = succesful_request(response)

    save_to_session('success', success)
    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/')

@app.route("/register", methods=['POST'])
def register():

    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is succesful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================

    response = requests.post(f"{AUTH_SERVICE_URL}/register", json={"username": req_username, "password": req_password})

    success = succesful_request(response)

    save_to_session('success', success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/')

@app.route('/invites', methods=['GET'])
def invites():
    #==============================
    # FEATURE (list invites)
    #
    # retrieve a list with all events you are invited to and have not yet responded to
    #==============================

    inviteList = requests.get(f"{EVENT_SERVICE_URL}/get_invites", json={"username": username}).json()["invites"]
    my_invites = []
    for invite in inviteList:
        my_invites.append((invite["id"], invite["title"], invite["date"], invite["organizer"], invite["privacy"]))
    return render_template('invites.html', username=username, password=password, invites=my_invites)

@app.route('/invites', methods=['POST'])
def process_invite():
    eventId, status = request.json['event'], request.json['status']

    #=======================
    # FEATURE (process invite)
    #
    # process an invite (accept, maybe, don't accept)
    #=======================

    requests.post(f"{EVENT_SERVICE_URL}/update_invites", json={"event_id": eventId, "status": status, "username": username})

    return redirect('/invites')

@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect('/')
