# server/routes.py
from flask import Blueprint, jsonify, request, session, current_app as app
from .extensions import db, bcrypt, mail  # Import db from extensions
from .models import User, Project, Cohort, ProjectMember
from flask_jwt_extended import create_access_token
from flask_mail import Message
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return jsonify({"message": "🗂️ Welcome to the Project Tracker API 🗂️"})

# ---------- Authentication Routes ----------

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    admin_secret = data.get('adminSecret')

    # Basic validation
    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    # Check if user should be admin
    is_admin = admin_secret == app.config.get('ADMIN_SECRET') if admin_secret else False

    # Create and save user
    new_user = User(
        username=username,
        email=email,
        password=bcrypt.generate_password_hash(password).decode('utf-8'),
        is_admin=is_admin
    )
    db.session.add(new_user)
    db.session.commit()
    new_user.generate_verification_code()
    send_verification_email(new_user.email, new_user.verification_code)

    return jsonify({"message": "User registered successfully. Check your email for verification code"}), 201


@main.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    code_entered = data.get('verification_code')
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.is_verified:
        return jsonify({"message": "User already verified"}), 200
    if user.verify_user(code_entered):
        return jsonify({"message": "User verified successfully"}), 200
    return jsonify({"error": "Invalid verification code"}), 400

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        if user.is_verified:
            access_token = create_access_token(identity=user.id)
            session['user_id'] = user.id
            role = "Admin" if user.is_admin else "Student"
            # Return full user information including role and username
            return jsonify({
                "message": f"Login successful as {role}",
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin
                }
            }), 200
        return jsonify({"error": "Account not verified. Please verify your email"}), 403
    return jsonify({"error": "Invalid credentials"}), 401



@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200


def send_verification_email(recipient_email, code):
    msg = Message(
        subject="Your Verification Code",
        sender="yourapp@example.com",
        recipients=[recipient_email],
        body=f"Your verification code is: {code}"
    )
    mail.send(msg)

# ---------- Cohort Routes ----------

# ---------- Cohort Routes ----------

@main.route('/cohorts', methods=['GET'])
def get_cohorts():
    cohorts = Cohort.query.all()
    return jsonify([cohort.to_dict() for cohort in cohorts]), 200

@main.route('/cohorts', methods=['POST'])
def create_cohort():
    data = request.get_json()
    try:
        new_cohort = Cohort(
            name=data.get('name'),
            description=data.get('description'),
            start_date=datetime.fromisoformat(data.get('start_date')),
            end_date=datetime.fromisoformat(data.get('end_date')),
            number_of_students=data.get('number_of_students')
        )
        new_cohort.validate()
        db.session.add(new_cohort)
        db.session.commit()
        return jsonify(new_cohort.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@main.route('/cohorts/<int:id>', methods=['GET'])
def get_cohort(id):
    cohort = Cohort.query.get_or_404(id)
    return jsonify(cohort.to_dict()), 200

@main.route('/cohorts/<int:id>', methods=['PUT'])
def update_cohort(id):
    data = request.get_json()
    cohort = Cohort.query.get_or_404(id)
    cohort.name = data.get('name', cohort.name)
    cohort.description = data.get('description', cohort.description)
    cohort.start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else cohort.start_date
    cohort.end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else cohort.end_date
    cohort.number_of_students = data.get('number_of_students', cohort.number_of_students)
    db.session.commit()
    return jsonify(cohort.to_dict()), 200

@main.route('/cohorts/<int:id>', methods=['DELETE'])
def delete_cohort(id):
    cohort = Cohort.query.get_or_404(id)
    db.session.delete(cohort)
    db.session.commit()
    return jsonify({"message": "Cohort deleted"}), 204

# ---------- Project Routes ----------

@main.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects]), 200

@main.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    try:
        new_project = Project(
            name=data.get('name'),
            description=data.get('description'),
            github_url=data.get('github_url'),
            type=data.get('type'),
            image_url=data.get('image_url')
        )
        new_project.validate()
        db.session.add(new_project)
        db.session.commit()
        return jsonify(new_project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@main.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = Project.query.get_or_404(id)
    return jsonify(project.to_dict()), 200

@main.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    data = request.get_json()
    project = Project.query.get_or_404(id)
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    project.github_url = data.get('github_url', project.github_url)
    project.type = data.get('type', project.type)
    project.image_url = data.get('image_url', project.image_url)
    db.session.commit()
    return jsonify(project.to_dict()), 200

@main.route('/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 204

# ---------- Project Member Routes ----------

@main.route('/project_members', methods=['GET'])
def get_project_members():
    members = ProjectMember.query.all()
    return jsonify([member.to_dict() for member in members]), 200

@main.route('/project_members', methods=['POST'])
def create_project_member():
    data = request.get_json()
    try:
        new_member = ProjectMember(
            project_id=data.get('project_id'),
            cohort_id=data.get('cohort_id'),
            student_name=data.get('student_name'),
            role=data.get('role'),
            joined_at=datetime.fromisoformat(data.get('joined_at')) if data.get('joined_at') else datetime.utcnow()
        )
        new_member.validate()
        db.session.add(new_member)
        db.session.commit()
        return jsonify(new_member.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@main.route('/project_members/<int:id>', methods=['GET'])
def get_project_member(id):
    member = ProjectMember.query.get_or_404(id)
    return jsonify(member.to_dict()), 200

@main.route('/project_members/<int:id>', methods=['PUT'])
def update_project_member(id):
    data = request.get_json()
    member = ProjectMember.query.get_or_404(id)
    member.project_id = data.get('project_id', member.project_id)
    member.cohort_id = data.get('cohort_id', member.cohort_id)
    member.student_name = data.get('student_name', member.student_name)
    member.role = data.get('role', member.role)
    member.joined_at = datetime.fromisoformat(data.get('joined_at')) if data.get('joined_at') else member.joined_at
    db.session.commit()
    return jsonify(member.to_dict()), 200

@main.route('/project_members/<int:id>', methods=['DELETE'])
def delete_project_member(id):
    member = ProjectMember.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Project member deleted"}), 204

# @main.route('/cohorts', methods=['GET'])
# def get_cohorts():
#     cohorts = Cohort.query.all()
#     return jsonify([cohort.to_dict() for cohort in cohorts]), 200


# @main.route('/cohorts', methods=['POST'])
# def create_cohort():
#     data = request.get_json()
#     new_cohort = Cohort(
#         name=data.get('name'),
#         description=data.get('description'),
#         github_url=data.get('github_url'),
#         type=data.get('type'),
#         start_date=datetime.fromisoformat(data.get('start_date')),
#         end_date=datetime.fromisoformat(data.get('end_date'))
#     )
#     db.session.add(new_cohort)
#     db.session.commit()
#     return jsonify(new_cohort.to_dict()), 201


# @main.route('/cohorts/<int:id>', methods=['GET'])
# def get_cohort(id):
#     cohort = Cohort.query.get_or_404(id)
#     return jsonify(cohort.to_dict()), 200


# @main.route('/cohorts/<int:id>', methods=['PUT'])
# def update_cohort(id):
#     data = request.get_json()
#     cohort = Cohort.query.get_or_404(id)
#     cohort.name = data.get('name', cohort.name)
#     cohort.description = data.get('description', cohort.description)
#     cohort.github_url = data.get('github_url', cohort.github_url)
#     cohort.type = data.get('type', cohort.type)
#     cohort.start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else cohort.start_date
#     cohort.end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else cohort.end_date
#     db.session.commit()
#     return jsonify(cohort.to_dict()), 200


# @main.route('/cohorts/<int:id>', methods=['DELETE'])
# def delete_cohort(id):
#     cohort = Cohort.query.get_or_404(id)
#     db.session.delete(cohort)
#     db.session.commit()
#     return jsonify({"message": "Cohort deleted"}), 204

# # ---------- Project Routes ----------

# @main.route('/projects', methods=['GET'])
# def get_projects():
#     projects = Project.query.all()
#     return jsonify([project.to_dict() for project in projects]), 200


# @main.route('/projects', methods=['POST'])
# def create_project():
#     data = request.get_json()
#     new_project = Project(
#         name=data.get('name'),
#         description=data.get('description'),
#         github_url=data.get('github_url'),
#         type=data.get('type'),
#         cohort_id=data.get('cohort_id')
#     )
#     db.session.add(new_project)
#     db.session.commit()
#     return jsonify(new_project.to_dict()), 201


# @main.route('/projects/<int:id>', methods=['GET'])
# def get_project(id):
#     project = Project.query.get_or_404(id)
#     return jsonify(project.to_dict()), 200


# @main.route('/projects/<int:id>', methods=['PUT'])
# def update_project(id):
#     data = request.get_json()
#     project = Project.query.get_or_404(id)
#     project.name = data.get('name', project.name)
#     project.description = data.get('description', project.description)
#     project.github_url = data.get('github_url', project.github_url)
#     project.type = data.get('type', project.type)
#     project.cohort_id = data.get('cohort_id', project.cohort_id)
#     db.session.commit()
#     return jsonify(project.to_dict()), 200


# @main.route('/projects/<int:id>', methods=['DELETE'])
# def delete_project(id):
#     project = Project.query.get_or_404(id)
#     db.session.delete(project)
#     db.session.commit()
#     return jsonify({"message": "Project deleted"}), 204

# # ---------- Project Member Routes ----------

# @main.route('/project_members', methods=['GET'])
# def get_project_members():
#     members = ProjectMember.query.all()
#     return jsonify([member.to_dict() for member in members]), 200


# @main.route('/project_members', methods=['POST'])
# def create_project_member():
#     data = request.get_json()
#     new_member = ProjectMember(
#         project_id=data.get('project_id'),
#         user_id=data.get('user_id'),
#         role=data.get('role')
#     )
#     db.session.add(new_member)
#     db.session.commit()
#     return jsonify(new_member.to_dict()), 201


# @main.route('/project_members/<int:id>', methods=['GET'])
# def get_project_member(id):
#     member = ProjectMember.query.get_or_404(id)
#     return jsonify(member.to_dict()), 200


# @main.route('/project_members/<int:id>', methods=['PUT'])
# def update_project_member(id):
#     data = request.get_json()
#     member = ProjectMember.query.get_or_404(id)
#     member.project_id = data.get('project_id', member.project_id)
#     member.user_id = data.get('user_id', member.user_id)
#     member.role = data.get('role', member.role)
#     db.session.commit()
#     return jsonify(member.to_dict()), 200


# @main.route('/project_members/<int:id>', methods=['DELETE'])
# def delete_project_member(id):
#     member = ProjectMember.query.get_or_404(id)
#     db.session.delete(member)
#     db.session.commit()
#     return jsonify({"message": "Project member deleted"}), 204



