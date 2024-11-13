from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, jwt, mail, migrate, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints and routes
    from .routes import main
    app.register_blueprint(main)

    return app




# # server/__init__.py
# from flask import Flask
# from .config import Config  # Ensure Config is correctly imported
# from flask_cors import CORS
# from .extensions import db, jwt, mail, migrate, bcrypt  # Import extensions from extensions.py

# def create_app():
#     # Create and configure the app
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # Initialize extensions with the app
#     db.init_app(app)
#     jwt.init_app(app)
#     mail.init_app(app)
#     migrate.init_app(app, db)
#     bcrypt.init_app(app)
#     CORS(app)

#     # Register the blueprint for routes
#     from .routes import main
#     app.register_blueprint(main)

#     # Import models after initializing the app to avoid circular import
#     with app.app_context():
#         from .models import User, Project, Cohort, ProjectMember
#         db.create_all()

#     return app



