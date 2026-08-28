# Placement Interview Scheduler

> A full-stack placement interview scheduling system for coordinating students, companies, interview panels, rooms, and interview time slots.

The application provides a coordinator dashboard for viewing interview assignments, monitoring scheduled and unscheduled interviews, and handling scheduling constraints such as panel availability, room availability, and interview conflicts.

---

## 🚀 What This Project Does

Placement interview scheduling involves coordinating multiple resources at the same time.

This project provides a centralized system to manage:

| Resource     | Purpose                                        |
| ------------ | ---------------------------------------------- |
| Students     | Students participating in placement interviews |
| Companies    | Companies conducting interviews                |
| Panels       | Interviewers/panels assigned to interviews     |
| Rooms        | Physical rooms used for interviews             |
| Interviews   | Individual interview assignments               |
| Applications | Student-company application information        |
| Shortlists   | Students shortlisted by companies              |

The system keeps track of these relationships and helps maintain a valid interview schedule.

---

## ✨ Key Features

### Coordinator Dashboard

* View the current interview schedule
* See scheduled and unscheduled interviews
* View student, company, panel, room, and timing information
* Monitor the overall interview schedule from one place

### Scheduling

* Assign interviews to available time slots
* Consider panel availability
* Consider room availability
* Detect scheduling conflicts
* Maintain interview start and end times
* Track scheduled and unscheduled assignments

### Replanning

The project includes a dedicated replanning service for handling scheduling conflicts.

```text
backend/scheduler/services/replanner.py
```

The replanning logic can reorganize interview assignments when the existing schedule cannot accommodate all interviews.

---

## 📊 Data Management

The system manages the following data:

* Student management
* Company management
* Panel management
* Room management
* Interview assignments
* Shortlists
* Applications

---

## ⚙️ Backend

The backend provides:

* REST API
* Django ORM
* PostgreSQL database
* Database migrations
* Management command for generating scheduling data

---

## ⚛️ Frontend

The frontend provides:

* React dashboard
* Vite development environment
* Responsive scheduling interface
* API-driven data display

---

## 📸 Application Preview

### Coordinator Dashboard

The main dashboard provides an overview of the current interview schedule and allows the coordinator to monitor scheduled and unscheduled assignments.

> **Add your dashboard screenshot here**
>
> `docs/screenshots/dashboard.png`

### Interview Schedule

The schedule displays interview assignments along with information such as student, company, day, start time, end time, panel, room, and scheduling status.

> **Add your schedule screenshot here**
>
> `docs/screenshots/schedule.png`

---

## 🧠 Scheduling Logic

The core purpose of the application is to produce a usable interview schedule while respecting available resources.

The scheduler works with:

```text
Student
   ↓
Application / Shortlist
   ↓
Interview Assignment
   ↓
Time Slot
   ├── Panel
   └── Room
```

An interview can only be considered successfully scheduled when the required scheduling constraints can be satisfied.

### Constraints Considered

* Panel availability
* Room availability
* Existing interview assignments
* Interview timing
* Resource conflicts

If an interview cannot be accommodated, the system keeps it as an **unscheduled assignment** instead of treating the schedule as successfully completed.

This makes unresolved scheduling conflicts visible to the coordinator.

---

## 🔄 Replanning

The project separates the replanning logic from the API layer.

```text
backend/
└── scheduler/
    └── services/
        └── replanner.py
```

The replanning service is responsible for dealing with situations where the current allocation needs to be reconsidered.

This separation makes the scheduling logic easier to maintain independently from:

* Database models
* API endpoints
* Frontend components

---

## 🛠️ Technology Stack

| Layer           | Technology            |
| --------------- | --------------------- |
| Frontend        | React                 |
| Build Tool      | Vite                  |
| Language        | JavaScript            |
| Styling         | CSS                   |
| Backend         | Python / Django       |
| API             | Django REST Framework |
| ORM             | Django ORM            |
| Database        | PostgreSQL            |
| Version Control | Git / GitHub          |

---

## 📂 Project Structure

```text
Placement-Scheduler/
│
├── backend/
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── scheduler/
│   │   ├── migrations/
│   │   │
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── generate_data.py
│   │   │
│   │   ├── services/
│   │   │   └── replanner.py
│   │   │
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
│   │
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## ⚙️ Local Setup

### Prerequisites

Make sure you have the following installed:

* Python 3
* PostgreSQL
* Node.js
* npm
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/sadeedmahamood/placement-interview-scheduler.git
cd placement-interview-scheduler
```

---

## 🐍 Backend Setup

### 2. Create a Virtual Environment

```bash
cd backend
python -m venv env
```

### Windows PowerShell

```powershell
.\env\Scripts\Activate.ps1
```

If PowerShell blocks script execution, activate the environment using:

```powershell
.\env\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

The backend uses PostgreSQL as its database.

Make sure PostgreSQL is installed and running, then configure the database connection according to your local environment.

Keep database credentials and other secrets outside the public repository.

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Generate Scheduling Data

The project includes a Django management command for generating project data.

```bash
python manage.py generate_data
```

### 7. Start the Backend

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000/
```

---

## ⚛️ Frontend Setup

Open a second terminal from the project root.

```bash
cd frontend
```

### 8. Install Dependencies

```bash
npm install
```

### 9. Start the Frontend

```bash
npm run dev
```

Vite will display the local frontend URL in the terminal.

Open that URL in your browser.

---

## ▶️ Running the Complete Application

You need two terminals.

### Terminal 1 — Django Backend

```powershell
cd backend
.\env\Scripts\Activate.ps1
python manage.py runserver
```

### Terminal 2 — React Frontend

```bash
cd frontend
npm run dev
```

Then open the frontend URL provided by Vite.

---

## 🔌 API

The React frontend communicates with the Django backend through REST API endpoints.

The API handles scheduling-related data including:

* Students
* Companies
* Panels
* Rooms
* Interviews
* Scheduling status

API routing is defined in:

```text
backend/config/urls.py
backend/scheduler/urls.py
```

---

## 🗄️ Database & Models

The backend uses Django models and PostgreSQL to persist scheduling data.

The main entities include:

* Student
* Company
* Panel
* Room
* Interview
* Shortlist
* Application

Database schema changes are maintained through Django migrations:

```text
backend/scheduler/migrations/
```

---

## 🧪 Validation & Testing

### Django System Check

Run the following command to verify that the project configuration does not contain system-level errors:

```bash
python manage.py check
```

### Run Tests

```bash
python manage.py test
```

---

## 🔐 Security & Git

The repository excludes files that should not be committed, including:

* Python virtual environments
* `node_modules`
* Environment files
* Local database files
* Build/cache files
* IDE-specific files

Sensitive information such as database passwords, API keys, and secret keys should never be committed to the public repository.

---

## 🚧 Future Improvements

Some possible improvements for future versions:

* Authentication and role-based access control
* Advanced filtering and search
* Drag-and-drop schedule management
* More advanced conflict-resolution strategies
* Improved automated test coverage
* Deployment with hosted PostgreSQL
* CI/CD integration
* Notifications for unresolved scheduling conflicts

---

## 👨‍💻 Author

**Sadeed Mahamood**

Full Stack Developer
