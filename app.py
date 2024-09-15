from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import os
from itsdangerous import URLSafeTimedSerializer as Serializer

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:new_password@localhost/ai"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'lucky'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'firstie369@gmail.com'
app.config['MAIL_PASSWORD'] = 'kghi lqdd bktq lbpw'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
limiter = Limiter(key_func=get_remote_address, app=app)

# Utility functions
def generate_verification_token(email):
    s = Serializer(app.config['SECRET_KEY'])
    return s.dumps({'email': email})
    
def confirm_verification_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return None
    return data.get('email')

def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    verification_url = f'http://localhost:5000/verify/{token}'
    msg = Message('Email Verification', sender='your-email@example.com', recipients=[user_email])
    msg.body = f'Please verify your email by clicking the link: {verification_url}'
    mail.send(msg)

# Import routes
import routes

if __name__ == "__main__":
    app.run(debug=True)