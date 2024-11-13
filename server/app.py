from server import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)



# # app.py

# from flask import Flask, request, jsonify, session
# from config import Config  # Import the Config class for app configuration
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager, create_access_token
# from flask_mail import Mail, Message
# from flask_migrate import Migrate
# from datetime import timedelta, datetime
# from flask_bcrypt import Bcrypt
# import random
# import string

# # Initialize app and extensions
# app = Flask(__name__)
# app.config.from_object(Config)  # Load configuration from Config class

# db = SQLAlchemy(app)
# jwt = JWTManager(app)
# mail = Mail(app)
# migrate = Migrate(app, db)
# bcrypt = Bcrypt(app)
# CORS(app)

# # Models
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     is_admin = db.Column(db.Boolean, default=False)
#     is_verified = db.Column(db.Boolean, default=False)
#     verification_code = db.Column(db.String(6), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "is_admin": self.is_admin,
#             "is_verified": self.is_verified,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#         }

#     def generate_verification_code(self):
#         self.verification_code = ''.join(random.choices(string.digits, k=6))
#         db.session.commit()

#     def verify_user(self, code_entered):
#         if self.verification_code == code_entered:
#             self.is_verified = True
#             self.verification_code = None
#             db.session.commit()
#             return True
#         return False

# class Project(db.Model):
#     __tablename__ = 'projects'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text, nullable=False)
#     github_url = db.Column(db.String(200), nullable=False)
#     type = db.Column(db.String(50), nullable=False)
#     cohort_id = db.Column(db.Integer, db.ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     image_url = db.Column(db.String(255), nullable=True)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "description": self.description,
#             "github_url": self.github_url,
#             "type": self.type,
#             "cohort_id": self.cohort_id,
#             "created_at": self.created_at.isoformat() if self.created_at else None,
#             "image_url": self.image_url
#         }

# class Cohort(db.Model):
#     __tablename__ = 'cohorts'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), unique=True, nullable=False)
#     description = db.Column(db.String(50), nullable=False)
#     github_url = db.Column(db.String(50), nullable=False)
#     type = db.Column(db.String(50), nullable=False)
#     start_date = db.Column(db.Date, nullable=False)
#     end_date = db.Column(db.Date, nullable=False)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "description": self.description,
#             "github_url": self.github_url,
#             "type": self.type,
#             "start_date": self.start_date.isoformat() if self.start_date else None,
#             "end_date": self.end_date.isoformat() if self.end_date else None
#         }

# class ProjectMember(db.Model):
#     __tablename__ = 'project_members'
#     id = db.Column(db.Integer, primary_key=True)
#     project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
#     user_id = db.Column(db.Integer, nullable=False)
#     joined_at = db.Column(db.DateTime, default=datetime.utcnow)
#     role = db.Column(db.String(50))

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "project_id": self.project_id,
#             "user_id": self.user_id,
#             "joined_at": self.joined_at.isoformat() if self.joined_at else None,
#             "role": self.role
#         }

# # Routes
# @app.route('/')
# def home():
#     return jsonify({"message": "🗂️ Welcome to the Project Tracker API 🗂️"})

# # Authentication routes
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')

#     if not all([username, email, password]):
#         return jsonify({"error": "Username, email, and password are required"}), 400

#     if User.query.filter_by(email=email).first():
#         return jsonify({"error": "Email already exists"}), 409

#     new_user = User(username=username, email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'))
#     db.session.add(new_user)
#     db.session.commit()
#     new_user.generate_verification_code()
#     send_verification_email(email, new_user.verification_code)
#     return jsonify({"message": "User registered successfully. Check your email for verification code"}), 201

# @app.route('/verify', methods=['POST'])
# def verify():
#     data = request.get_json()
#     email = data.get('email')
#     code_entered = data.get('verification_code')
#     user = User.query.filter_by(email=email).first()

#     if not user:
#         return jsonify({"error": "User not found"}), 404
#     if user.is_verified:
#         return jsonify({"message": "User already verified"}), 200
#     if user.verify_user(code_entered):
#         return jsonify({"message": "User verified successfully"}), 200
#     return jsonify({"error": "Invalid verification code"}), 400

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     user = User.query.filter_by(email=email).first()

#     if user and bcrypt.check_password_hash(user.password, password):
#         if user.is_verified:
#             access_token = create_access_token(identity=user.id)
#             session['user_id'] = user.id
#             return jsonify({"message": "Login successful", "access_token": access_token}), 200
#         return jsonify({"error": "Account not verified. Please verify your email"}), 403
#     return jsonify({"error": "Invalid credentials"}), 401

# @app.route('/logout', methods=['POST'])
# def logout():
#     session.pop('user_id', None)
#     return jsonify({"message": "Logged out successfully"}), 200

# # Utility function
# def send_verification_email(recipient_email, code):
#     msg = Message(
#         subject="Your Verification Code",
#         sender="yourapp@example.com",
#         recipients=[recipient_email],
#         body=f"Your verification code is: {code}"
#     )
#     mail.send(msg)

# # Main function
# if __name__ == '__main__':
#     app.run(debug=True)
