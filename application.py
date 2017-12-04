from flask import Flask, flash, jsonify, render_template, request, url_for, session, redirect, abort
import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask_session import Session
from tempfile import mkdtemp
import os
import urllib.request
import requests
import json
from cs50 import SQL
from functools import wraps

db = SQL("sqlite:///bloodconnect.db")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['email', 'https://www.googleapis.com/auth/plus.login']
CLIENT_SECRETS_FILE = "client_secret.json"
API_SERVICE_NAME = 'oauth2'
API_VERSION = 'v2'

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("profile") is None:
            return redirect(url_for('authorize'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html", messages=get_donation_requests())


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    return redirect(authorization_url)


@app.route('/auth/callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    profileUrl = f"https://www.googleapis.com/userinfo/v2/me?access_token={credentials.token}"
    profileResponse = urllib.request.urlopen(profileUrl)
    session['profile'] = json.loads(profileResponse.read().decode('utf-8'))
    profileResponse.close()
    userInDb = db.execute("""SELECT * FROM user_profile
                        WHERE id=:id""", id=session['profile']['id'])
    if len(userInDb) == 0:
        execute = db.execute("INSERT INTO user_profile (ID, email, name, picture) VALUES (:id, :email, :name, :picture)",
                             id=session['profile']['id'],
                             email=session['profile']['email'],
                             name=session['profile']['name'],
                             picture=session['profile']['picture'])

    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('index'))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


@app.route('/clear')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    if 'profile' in session:
        del session['profile']
    return redirect(url_for('index'))


@app.route('/revoke')
@login_required
def revoke():
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        flash('Revoked successfully.')
        return redirect(url_for('clear_credentials'))
    else:
        flash('An error occurred.')
        return redirect(url_for('index'))


@app.route('/register-donor', methods=["GET", "POST"])
@login_required
def register_donor():
    if request.method == "POST":
        if not request.form.get("blood-group"):
            flash("blood group  needed for registration")
        else:
            execute = db.execute("UPDATE user_profile set blood_group=:blood_group where ID=:id",
                                 blood_group=request.form.get("blood-group"),
                                 id=session['profile']['id'])
            if not execute:
                flash("Server error while registering")
            else:
                flash("Registered successfully!!!")
    return render_template("register-donor.html")


@app.route('/notify-donors', methods=["GET", "POST"])
@login_required
def notify_donors():
    if request.method == "POST":
        blood_groups = request.form.getlist('blood-group')
        message = request.form.get('message')
        title = request.form.get('title')
        execute = db.execute("""INSERT into donation_requests
                              (CREATED_BY, MESSAGE, TITLE, A_POS, A_NEG, B_POS, B_NEG, O_POS, O_NEG, AB_POS, AB_NEG)
                              VALUES
                              (:created_by, :message, :title, :a_pos, :a_neg, :b_pos, :b_neg, :o_pos, :o_neg, :ab_pos, :ab_neg)""",
                             created_by=session['profile']['id'],
                             message=message,
                             title=title,
                             a_pos=int('A+' in blood_groups),
                             a_neg=int('A-' in blood_groups),
                             b_pos=int('B+' in blood_groups),
                             b_neg=int('B-' in blood_groups),
                             o_pos=int('O+' in blood_groups),
                             o_neg=int('O-' in blood_groups),
                             ab_pos=int('AB+' in blood_groups),
                             ab_neg=int('AB-' in blood_groups))
        if not execute:
            flash("Server error while saving donation request")
        else:
            flash("Request saved and visible to all donors!!!")
    return render_template("notify-donors.html")


@app.route('/archive-request/<message_id>', methods=["DELETE"])
@login_required
def archive_message(message_id):
    if not message_id:
        return abort(400)
    else:
        execute = db.execute(
            "UPDATE donation_requests set ARCHIVE=1 where ID=:message_id", message_id=message_id)
        if not execute:
            return abort(500)
        else:
            return jsonify({"deleted": "true"})


def get_donation_requests():
    if session.get("profile") is None:
        return []
    rows = db.execute("""SELECT donation_requests.ID as messageId,
                       user_profile.name as name,
                       user_profile.email as email,
                       user_profile.ID as profileId,
                       donation_requests.MODIFIED_AT as messageCreated,
                       donation_requests.TITLE as title,
                       donation_requests.MESSAGE as message,
                       donation_requests.A_POS as a_pos,
                       donation_requests.A_NEG as a_neg,
                       donation_requests.B_POS as b_pos,
                       donation_requests.B_NEG as b_neg,
                       donation_requests.O_POS as o_pos,
                       donation_requests.O_NEG as o_neg,
                       donation_requests.AB_POS as ab_pos,
                       donation_requests.AB_NEG as ab_neg
                       FROM donation_requests
                       join user_profile on donation_requests.CREATED_BY=user_profile.ID
                       where donation_requests.ARCHIVE=0 ORDER BY messageCreated DESC""")
    return rows
