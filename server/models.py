from datetime import datetime
import random
import string
from .extensions import db
from sqlalchemy.exc import IntegrityError

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def generate_verification_code(self):
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        db.session.commit()

    def verify_user(self, code_entered):
        if self.verification_code == code_entered:
            self.is_verified = True
            self.verification_code = None
            db.session.commit()
            return True
        return False


class Cohort(db.Model):
    __tablename__ = 'cohorts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    number_of_students = db.Column(db.Integer, nullable=False)

    # Relationship with ProjectMember
    project_members = db.relationship('ProjectMember', back_populates='cohort', cascade='all, delete-orphan', lazy='select')

    def __repr__(self):
        return f"<Cohort {self.name} (Students: {self.number_of_students})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "number_of_students": self.number_of_students,
            "project_members": [member.to_dict() for member in self.project_members]
        }

    def validate(self):
        if len(self.name) < 3:
            raise ValueError("Cohort name must be at least 3 characters long.")
        if self.number_of_students <= 0:
            raise ValueError("Cohort must have a positive number of students.")


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    github_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    # Relationship with ProjectMember
    project_members = db.relationship('ProjectMember', back_populates='project', cascade='all, delete-orphan', lazy='select')

    def __repr__(self):
        return f"<Project {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "github_url": self.github_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "type": self.type,
            "image_url": self.image_url,
            "project_members": [member.to_dict() for member in self.project_members]
        }

    def validate(self):
        if len(self.name) < 3:
            raise ValueError("Project name must be at least 3 characters long.")
        if len(self.description) < 10:
            raise ValueError("Description must be at least 10 characters long.")
        if not self.github_url.startswith('http'):
            raise ValueError("Invalid GitHub URL format.")


class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    cohort_id = db.Column(db.Integer, db.ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', back_populates='project_members')
    cohort = db.relationship('Cohort', back_populates='project_members')

    def __repr__(self):
        return f"<ProjectMember (Project: {self.project_id}, Cohort: {self.cohort_id}, Student: {self.student_name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_name": self.student_name,
            "role": self.role,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "project_id": self.project_id,
            "cohort_id": self.cohort_id
        }

    def validate(self):
        if len(self.student_name) < 3:
            raise ValueError("Student name must be at least 3 characters long.")
        if len(self.role) < 3:
            raise ValueError("Role must be at least 3 characters long.")


def handle_integrity_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Integrity error: Something went wrong with the database.")
    return wrapper


@handle_integrity_error
def add_cohort(cohort):
    cohort.validate()
    db.session.add(cohort)
    db.session.commit()

@handle_integrity_error
def add_project(project):
    project.validate()
    db.session.add(project)
    db.session.commit()

@handle_integrity_error
def add_project_member(project_member):
    project_member.validate()
    db.session.add(project_member)
    db.session.commit()


