import os
import hashlib
import base64
import logging
import mysql.connector
from flask import Flask, request, redirect, url_for, session, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from flask_session import Session
import msal
import secrets
import subprocess
from PIL import Image
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to your actual secret key
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set the client secret in the environment variables before running the app
#os.environ['CLIENT_SECRET'] = ''

# Azure AD Config
CLIENT_ID = ''
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTHORITY = ''
REDIRECT_PATH = '/getAToken'
SCOPE = ["User.Read"]
SESSION_TYPE = 'filesystem'
logging.basicConfig(level=logging.DEBUG)

# MySQL Config
DB_HOST = ''
DB_USER = ''
DB_PASSWORD = ''
DB_NAME = ''

def get_db_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

def generate_code_verifier():
    """Generates a code verifier for PKCE"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    logging.debug(f"Generated code_verifier: {code_verifier}")
    return code_verifier

def generate_code_challenge(code_verifier):
    """Generates a code challenge for PKCE"""
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip('=')
    logging.debug(f"Generated code_challenge: {code_challenge} for code_verifier: {code_verifier}")
    return code_challenge

@app.route('/')
def index():
    logging.debug("Index page accessed")
    if not session.get("user"):
        logging.debug("No user in session, redirecting to login")
        return redirect(url_for("login"))
    logging.debug("User found in session, redirecting to upload_form")
    return redirect(url_for("upload_form"))

@app.route('/login')
def login():
    logging.debug("Login page accessed")
    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    logging.debug(f"Authorization flow initiated: {session['flow']}")
    return redirect(session["flow"]["auth_uri"])

@app.route(REDIRECT_PATH)
def authorized():
    logging.debug("Redirect path accessed")
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=SCOPE,
            redirect_uri=url_for('authorized', _external=True))
        if "error" in result:
            logging.error(f"Error acquiring token: {result.get('error_description')}")
            return f"Error acquiring token: {result.get('error_description')}", 400
        session["user"] = result.get("id_token_claims")
        logging.debug(f"User {session['user']} authenticated")
        _save_cache(cache)

        # Store user info in the database
        user_email = session["user"].get("preferred_username")
        user_name = session["user"].get("name")
        logging.debug(f"Storing user info: email={user_email}, name={user_name}")
        store_user_info(user_email, user_name)
        
    except ValueError as e:  # Usually caused by CSRF
        logging.error(f"ValueError: {e}")
        pass  # Simply ignore them
    return redirect(url_for("index"))

def store_user_info(email, name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=%s", (email, name, name))
        connection.commit()
        cursor.close()
        connection.close()
        logging.debug("User info stored successfully")
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return

@app.route('/logout')
def logout():
    logging.debug("Logout page accessed")
    session.clear()
    return redirect(
        'https://login.microsoftonline.com/common/oauth2/v2.0/logout' +
        '?post_logout_redirect_uri=' + url_for('index', _external=True))

@app.route('/upload_form')
def upload_form():
    logging.debug("Upload form page accessed")
    if not session.get("user"):
        logging.debug("No user in session, redirecting to login")
        return redirect(url_for("login"))
    
    user_email = session["user"].get("preferred_username")
    uploads = get_user_uploads(user_email)
    
    return render_template('upload.html', uploads=uploads)

def get_user_uploads(email):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT upload_time, image_file FROM uploads WHERE user_email = %s ORDER BY upload_time DESC", (email,))
        uploads = cursor.fetchall()
        cursor.close()
        connection.close()
        logging.debug(f"User uploads retrieved successfully for {email}")
        return uploads
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return []


@app.route('/upload', methods=['POST'])
def upload_image():
    logging.debug("Upload image request received")
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Store upload details in the database
        user_email = session["user"].get("preferred_username")
        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        store_upload_details(user_email, upload_time, filename)

        return redirect(url_for('roi_selector', filename=filename))

def store_upload_details(email, upload_time, filename):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uploads (user_email, upload_time, image_file) VALUES (%s, %s, %s)", (email, upload_time, filename))
        connection.commit()
        cursor.close()
        connection.close()
        logging.debug("Upload details stored successfully")
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    logging.debug(f"Uploaded file {filename} requested")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/roi_selector')
def roi_selector():
    logging.debug("ROI selector page accessed")
    if not session.get("user"):
        logging.debug("No user in session, redirecting to login")
        return redirect(url_for("login"))
    filename = request.args.get('filename')
    return render_template('roi_selector.html', filename=filename)

@app.route('/crop', methods=['POST'])
def crop_image():
    logging.debug("Crop image request received")
    data = request.json
    filename = data['filename']
    x = data['x']
    y = data['y']
    width = data['width']
    height = data['height']

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(image_path)
    cropped_image = image.crop((x, y, x + width, y + height))
    cropped_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cropped_' + filename)
    cropped_image.save(cropped_image_path)

    # Execute the scripts in order: main.py -> process.py -> process2.py
    subprocess.run(['python', 'main.py', cropped_image_path, 'output.txt'], check=True)
    subprocess.run(['python', 'process.py', 'output.txt', 'static/output.csv'], check=True)
    subprocess.run(['python', 'process2.py', 'static/output.csv', 'static/plot.png'], check=True)
    
    return jsonify({"message": "Image cropped and processed successfully."}), 200

@app.route('/dashboard')
def dashboard():
    logging.debug("Dashboard page accessed")
    if not session.get("user"):
        logging.debug("No user in session, redirecting to login")
        return redirect(url_for("login"))
    return render_template('dashboard.html')

def _build_auth_code_flow(authority=None, scopes=None):
    code_verifier = generate_code_verifier()
    session['code_verifier'] = code_verifier
    logging.debug(f"Storing code_verifier in session: {session['code_verifier']}")
    code_challenge = generate_code_challenge(code_verifier)
    logging.debug(f"Generated code_challenge: {code_challenge}")

    auth_url = _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        redirect_uri=url_for('authorized', _external=True),
        code_challenge=code_challenge,
        code_challenge_method="S256")

    return {"auth_uri": auth_url}

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority or AUTHORITY,
        client_credential=CLIENT_SECRET,
        token_cache=cache)

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get('token_cache'):
        cache.deserialize(session['token_cache'])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session['token_cache'] = cache.serialize()

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='localhost', port=5000, debug=True)
