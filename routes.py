from app import app, db, mail, generate_verification_token, confirm_verification_token, send_verification_email
from flask import request, jsonify
from models import User, Profile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiting
limiter = Limiter(key_func=get_remote_address, app=app)

# Registration Route
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

# Email Verification Route
@app.route("/verify/<token>")
def verify_email(token):
    email = confirm_verification_token(token)
    if email is None:
        return jsonify({"error": "Verification link is invalid or has expired"}), 400

    user = User.query.filter_by(email=email).first_or_404()
    user.email_verified = True
    db.session.commit()

    return jsonify({"message": "Email verified successfully!"}), 200

# Login Route
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

    token = generate_verification_token(email)  # You can use the same function to generate a token
    return jsonify({"message": "Login successful!", "token": token}), 200

# Get User Profile Route
@app.route("/profile", methods=["GET"])
@limiter.limit("5 per minute")
def get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    user_email = confirm_verification_token(token)
    if not user_email:
        return jsonify({"error": "Invalid or expired token"}), 401

    user = User.query.filter_by(email=user_email).first_or_404()
    profile = Profile.query.filter_by(user_id=user.id).first()

    return jsonify({
        "username": user.username,
        "email": user.email,
        "bio": profile.bio if profile else None,
        "profile_picture": profile.profile_picture if profile else None
    }), 200

# Update User Profile Route
@app.route("/profile", methods=["POST"])
@limiter.limit("5 per minute")
def update_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    user_email = confirm_verification_token(token)
    if not user_email:
        return jsonify({"error": "Invalid or expired token"}), 401

    user = User.query.filter_by(email=user_email).first_or_404()
    profile = Profile.query.filter_by(user_id=user.id).first()

    data = request.json
    bio = data.get("bio")
    profile_picture = data.get("profile_picture")

    if profile:
        profile.bio = bio
        profile.profile_picture = profile_picture
    else:
        profile = Profile(user_id=user.id, bio=bio, profile_picture=profile_picture)
        db.session.add(profile)

    db.session.commit()

    return jsonify({"message": "Profile updated successfully!"}), 200