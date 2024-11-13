# server/config.py
import os

class Config:
    # Define the base directory for the project (where this file is located)
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Application secrets
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret-key")
    ADMIN_SECRET = os.getenv("ADMIN_SECRET", "fallback-admin-secret")  # Add ADMIN_SECRET here

    # Database Configuration - Ensure it points to kin.db in the server/instance folder
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'kin.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

