# server/extensions.py
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_mail import Mail

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# mail = Mail()

# server/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# Initialize extensions without attaching them to the app instance
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
bcrypt = Bcrypt()
