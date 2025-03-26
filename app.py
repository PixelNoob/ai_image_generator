import os
import json
import requests
import base64
from flask import Flask, render_template, request, Response, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "200 per hour"]
)

## database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
#users = {
#    "admin": {
#        "password": generate_password_hash(os.getenv("password"))  # Hashed password
#    }
#}

## real db
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    latest_image = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

#register form
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

@app.route("/", methods=["GET", "POST"])
@login_required  # Protect the route, only logged-in users can access it
def index():
    global latest_image

    if request.method == "POST":
        image_prompt = request.form["image"]

        payload = {
            "model": "flux-dev", #pony-realism
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
            current_user.latest_image = response_json["images"][0]
            db.session.commit()

    return render_template("index.html", latest_image=(current_user.latest_image is not None))

@app.route("/image")
@login_required
def get_image():
    if current_user.latest_image:
        image_data = base64.b64decode(current_user.latest_image)
        return Response(image_data, mimetype="image/png")
    return "No image generated yet.", 404

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
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

@app.route("/test")
def test():
    return "This is a test endpoint."

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "warning")
        else:
            new_user = User(
                username=username,
                password=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Registration successful!", "success")
            return redirect(url_for("index"))

    return render_template("register.html", form=form)


#create database once, then comment
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)