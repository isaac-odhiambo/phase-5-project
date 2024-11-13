import os
import sys
from datetime import datetime
from faker import Faker
import random

# Add the parent directory of `server` to sys.path to ensure the `server` module is recognized
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import create_app, db
from server.models import User, Project, Cohort, ProjectMember

# Initialize the app and Faker
app = create_app()
faker = Faker()

with app.app_context():
    # Delete existing records from tables
    ProjectMember.query.delete()
    Project.query.delete()
    Cohort.query.delete()
    User.query.delete()

    # Commit the deletions
    db.session.commit()

    # Seed Users (Optional if you have a user model and want to seed it)
    users = []
    for _ in range(5):
        user = User(
            username=faker.user_name(),
            email=faker.email(),
            password="hashed_password",  # Replace with an actual hashed password in a real scenario
            is_admin=random.choice([True, False]),
            created_at=faker.date_time_this_year()
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()

    # Seed Cohorts
    cohorts = []
    current_year = datetime.now().year
    for i in range(5):
        cohort_name = f"{random.choice(['FT', 'PT'])}-{i + 1}/{current_year}"
        cohort = Cohort(
            name=cohort_name,
            description=faker.sentence(),
            start_date=faker.date_this_year(before_today=True, after_today=False),
            end_date=faker.date_this_year(before_today=False, after_today=True),
            number_of_students=random.randint(20, 50),
        )
        db.session.add(cohort)
        cohorts.append(cohort)
    db.session.commit()

    # Seed Projects and link them to Cohorts
    projects = []
    for _ in range(100):  # Updated to create 100 projects
        cohort = random.choice(cohorts)
        project = Project(
            name=faker.sentence(nb_words=3),
            description=faker.paragraph(),
            github_url=faker.url(),
            type=random.choice(["Research", "Development"]),
            created_at=faker.date_this_year(),
            image_url=faker.image_url()
        )
        db.session.add(project)
        projects.append((project, cohort))
    db.session.commit()

    # Seed Project Members for each Project
    for project, cohort in projects:
        for _ in range(random.randint(3, 5)):
            project_member = ProjectMember(
                project_id=project.id,
                cohort_id=cohort.id,
                student_name=faker.name(),
                role=random.choice(["Developer", "Tester", "Project Manager"]),
                joined_at=faker.date_time_this_year()
            )
            db.session.add(project_member)

    db.session.commit()

    print("Database seeded successfully with users, cohorts, projects, and project members.")




# # server/seed.py
# from server import create_app, db
# from server.models import User, Project, Cohort, ProjectMember
# from datetime import datetime
# from faker import Faker
# import random

# # Initialize the app and Faker
# app = create_app()
# faker = Faker()

# with app.app_context():
#     # Delete existing records from tables
#     ProjectMember.query.delete()
#     Project.query.delete()
#     Cohort.query.delete()
#     User.query.delete()

#     # Commit the deletions
#     db.session.commit()

#     # Seed Users (Optional if you have a user model and want to seed it)
#     users = []
#     for _ in range(5):
#         user = User(
#             username=faker.user_name(),
#             email=faker.email(),
#             password="hashed_password",  # Replace with an actual hashed password in a real scenario
#             is_admin=random.choice([True, False]),
#             created_at=faker.date_time_this_year()
#         )
#         db.session.add(user)
#         users.append(user)
#     db.session.commit()

#     # Seed Cohorts
#     cohorts = []
#     current_year = datetime.now().year
#     for i in range(5):
#         cohort_name = f"{random.choice(['FT', 'PT'])}-{i + 1}/{current_year}"
#         cohort = Cohort(
#             name=cohort_name,
#             description=faker.sentence(),
#             start_date=faker.date_this_year(before_today=True, after_today=False),
#             end_date=faker.date_this_year(before_today=False, after_today=True),
#             number_of_students=random.randint(20, 50),
#         )
#         db.session.add(cohort)
#         cohorts.append(cohort)
#     db.session.commit()

#     # Seed Projects and link them to Cohorts
#     projects = []
#     for _ in range(10):
#         cohort = random.choice(cohorts)
#         project = Project(
#             name=faker.sentence(nb_words=3),
#             description=faker.paragraph(),
#             github_url=faker.url(),
#             type=random.choice(["Research", "Development"]),
#             created_at=faker.date_this_year(),
#             image_url=faker.image_url()
#         )
#         db.session.add(project)
#         projects.append((project, cohort))
#     db.session.commit()

#     # Seed Project Members for each Project
#     for project, cohort in projects:
#         for _ in range(random.randint(3, 5)):
#             project_member = ProjectMember(
#                 project_id=project.id,
#                 cohort_id=cohort.id,
#                 student_name=faker.name(),
#                 role=random.choice(["Developer", "Tester", "Project Manager"]),
#                 joined_at=faker.date_time_this_year()
#             )
#             db.session.add(project_member)

#     db.session.commit()

#     print("Database seeded successfully with users, cohorts, projects, and project members.")

