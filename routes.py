from app import app, db, mail, generate_verification_token, confirm_verification_token, send_verification_email
from flask import request, jsonify
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiting
limiter = Limiter(key_func=get_remote_address, app=app)

@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use"}), 400

    hashed_password = generate_password_hash(password, method='scrypt')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    send_verification_email(email)

    return jsonify({"message": "User registered successfully! Please check your email to verify your account."}), 201

@app.route("/verify/<token>")
def verify_email(token):
    email = confirm_verification_token(token)
    if email is None:
        return jsonify({"error": "Verification link is invalid or has expired"}), 400

    user = User.query.filter_by(email=email).first_or_404()
    user.email_verified = True
    db.session.commit()

    return jsonify({"message": "Email verified successfully!"}), 200

@app.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.email_verified:
        return jsonify({"error": "Email not verified. Please verify your email before logging in."}), 403

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful!"}), 200

def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    verification_url = f'http://localhost:5000/verify/{token}'
    msg = Message('Email Verification', sender='your-email@example.com', recipients=[user_email])
    msg.body = f'Please verify your email by clicking the link: {verification_url}'
    mail.send(msg)