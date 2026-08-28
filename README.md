# Placement Interview Scheduler

A full-stack web application for managing and scheduling placement interviews for students, companies, interview panels, and rooms.

The system provides a coordinator dashboard where interview assignments can be viewed and managed while considering scheduling constraints such as panel availability, room availability, company requirements, and interview conflicts.

## Features

- View the current interview schedule from a coordinator dashboard
- Display scheduled and unscheduled interviews
- Manage students, companies, panels, rooms, and interview assignments
- Handle interview scheduling constraints
- Track panel availability
- Track room allocation
- Identify scheduling conflicts
- Automatically generate placement scheduling data
- Replan interview assignments when scheduling conflicts occur
- REST API powered backend
- React-based frontend dashboard

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- Django ORM

### Frontend

- React
- Vite
- JavaScript
- CSS

### Development Tools

- Git
- GitHub
- VS Code

## Project Structure

Placement-Scheduler/
│
├── backend/
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── scheduler/
│   │   ├── migrations/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── generate_data.py
│   │   ├── services/
│   │   │   └── replanner.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── requirements.txt
│   └── manage.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
System Architecture

Scheduling Approach

The scheduler works with the different entities involved in placement interviews:

Students
Companies
Interview panels
Rooms
Interview assignments

The scheduling process considers resource availability and existing interview assignments.

When conflicts occur, the replanning service can be used to reorganize interview assignments while respecting the available scheduling resources.

The backend contains the scheduling/replanning logic separately under:

backend/scheduler/services/replanner.py

This keeps the scheduling logic separate from the API and database layers.

Backend Setup
1. Clone the repository
git clone https://github.com/sadeedmahamood/placement-interview-scheduler.git
cd placement-interview-scheduler
2. Create a Python virtual environment

From the project root:

cd backend
python -m venv env

Activate it on Windows:

.\env\Scripts\Activate.ps1

If PowerShell execution policy prevents activation, the environment can also be activated using:

.\env\Scripts\activate
3. Install Python dependencies
pip install -r requirements.txt
4. Configure the database

The project uses PostgreSQL.

Make sure PostgreSQL is installed and running, then configure the database connection in the Django settings/environment according to your local setup.

Do not commit database passwords, API keys, or other secrets to GitHub.

5. Run migrations
python manage.py migrate
6. Generate project data

The project includes a management command for generating scheduling data:

python manage.py generate_data
7. Start the Django server
python manage.py runserver

The backend will normally be available at:

http://127.0.0.1:8000/
Frontend Setup

Open a second terminal and navigate to the frontend:

cd frontend
1. Install dependencies
npm install
2. Start the development server
npm run dev

Vite will provide the local development URL in the terminal.

Running the Full Application

Start the backend:

cd backend
.\env\Scripts\Activate.ps1
python manage.py runserver

Then start the frontend in a separate terminal:

cd frontend
npm run dev

Open the frontend URL provided by Vite in your browser.

API

The Django backend exposes REST API endpoints used by the React frontend.

The API is responsible for providing and managing scheduling-related information such as:

Interview assignments
Students
Companies
Panels
Rooms
Scheduling status

The API routes are defined in:

backend/config/urls.py
backend/scheduler/urls.py
Data Model

The backend contains models representing the main entities involved in the scheduling system.

These include:

Student
Company
Panel
Room
Interview
Shortlist
Application

Database migrations are maintained under:

backend/scheduler/migrations/
Validation and Conflict Handling

The scheduler is designed to identify situations where interview assignments cannot be scheduled because of resource or scheduling constraints.

Examples include:

Panel availability conflicts
Room availability conflicts
Conflicting interview assignments
Scheduling assignments that cannot be accommodated

The system distinguishes between scheduled and unscheduled interview assignments so that coordinators can identify assignments that require attention.

Testing

Django's test framework is available through:

python manage.py test

Django system checks can also be run using:

python manage.py check
Environment and Security

Sensitive configuration should be stored in environment variables or local configuration files rather than committed to Git.

The repository's .gitignore excludes:

Python virtual environments
Node.js node_modules
Environment files
Django database files
Build/cache files
IDE-specific files
Future Improvements

Possible future improvements include:

Authentication and role-based access control
Drag-and-drop schedule management
Advanced filtering and search
Improved conflict-resolution strategies
Deployment with a hosted PostgreSQL database
Automated CI/CD
More comprehensive automated tests
Coordinator notifications for unresolved scheduling conflicts
Author

Sadeed Mahamood

Full Stack Developer

GitHub:
https://github.com/sadeedmahamood


### One important correction before you paste it

Because this is going to be a **public repository**, I don't want us blindly assuming the exact PostgreSQL/environment configuration in your `settings.py`.

Your code is already pushed safely. **Next, I recommend we inspect `backend/config/settings.py` and `requirements.txt` once**, make sure the README's setup instructions exactly match your project, and then I'll give you the final README to commit.

That avoids a reviewer cloning the repository and hitting a setup error because the README says something slightly different from your actual configuration.
