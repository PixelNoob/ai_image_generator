import os
import json
import requests
import base64
from flask import Flask, render_template, request, Response, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# API Details
API_URL = "https://api.venice.ai/api/v1/image/generate"
API_KEY = os.getenv("venice")

# Set up Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"  # Redirect users who are not logged in
login_manager.init_app(app)

# Store the last generated image
latest_image = None

# Dummy user database (Replace with a real database later)
users = {
    "admin": {
        "password": generate_password_hash(os.getenv("password"))  # Hashed password
    }
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    """Load user from dictionary"""
    if username in users:
        return User(username)
    return None

# Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route("/", methods=["GET", "POST"])
@login_required  # Protect the route, only logged-in users can access it
def index():
    global latest_image

    if request.method == "POST":
        image_prompt = request.form["image"]

        payload = {
            "model": "fluently-xl",
            "prompt": image_prompt,
            "width": 512,
            "height": 512
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            latest_image = response_json["images"][0]

    return render_template("index.html", latest_image=(latest_image is not None))

@app.route("/image")
@login_required
def get_image():
    """Serve the latest generated image as a PNG."""
    global latest_image
    if latest_image:
        image_data = base64.b64decode(latest_image)
        return Response(image_data, mimetype="image/png")
    return "No image generated yet.", 404

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users and check_password_hash(users[username]["password"], password):
            user = User(username)
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    """Logout the user"""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
