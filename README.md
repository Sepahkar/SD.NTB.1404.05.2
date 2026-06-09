# ⚡ NTBIAU Panel

Welcome to the **NTBIAU Panel** project. This repository is built using Django and Django REST Framework (DRF), complete with OpenAPI & Swagger documentation.

---

## 🚀 Getting Started & Setup

Follow these steps to set up and run the project locally on your machine.

### 1. Clone the Repository
```bash
git clone https://github.com/Sepahkar/SD.NTB.1404.05.2.git
cd SD.NTB.1404.05.2
```

### 2. Set Up Virtual Environment
Ensure you have Python installed, then create and activate the virtual environment:
```bash
# Create virtual environment (if not already present)
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (cmd):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
Apply the existing database migrations:
```bash
python manage.py migrate
```

### 5. Run Development Server
```bash
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## 🔐 Administrative Access

The project has a pre-configured admin account to access the Django Administration Panel.

* **Admin URL:** `http://127.0.0.1:8000/admin/`
* **Username:** `admin`
* **Password:** `root@!123`

---

## 📄 API Documentation

We use `drf-spectacular` to auto-generate OpenAPI 3 schemas and interactive documentations. When the server is running, you can access the following:

| Path | Description |
| :--- | :--- |
| [`/api/schema/`](http://127.0.0.1:8000/api/schema/) | The raw OpenAPI JSON schema endpoint |
| [`/api/docs/`](http://127.0.0.1:8000/api/docs/) | **Swagger UI** - Interactive UI to explore and test the endpoints |
| [`/api/redoc/`](http://127.0.0.1:8000/api/redoc/) | **ReDoc UI** - Elegant, three-column layout documentation |

### Example API Endpoint
* **Ping / Health Check:** [`http://127.0.0.1:8000/api/ping/`](http://127.0.0.1:8000/api/ping/)

---

## 🛠️ Common & Useful Django Commands

Here are the most frequently used commands during development.

### 🖥️ Development Server
* **Run Server (Default Port 8000):**
  ```bash
  python manage.py runserver
  ```
* **Run Server on Custom Port / Host:**
  ```bash
  python manage.py runserver 0.0.0.0:8080
  ```

### 🗄️ Database Management & Migrations
* **Create Migrations:** (Runs after you modify model definitions)
  ```bash
  python manage.py makemigrations
  ```
* **Create Migrations for specific App:**
  ```bash
  python manage.py makemigrations <app_name>
  ```
* **Apply Migrations:** (Syncs database state with migrations files)
  ```bash
  python manage.py migrate
  ```
* **Show Migration Status:**
  ```bash
  python manage.py showmigrations
  ```
* **Inspect Database Changes SQL:** (Inspects what SQL commands a migration will execute)
  ```bash
  python manage.py sqlmigrate <app_name> <migration_number>
  ```

### 👤 User Management
* **Create a Superuser:** (Creates a new administrative account)
  ```bash
  python manage.py createsuperuser
  ```
* **Change Password:**
  ```bash
  python manage.py changepassword <username>
  ```

### 🧪 Testing & Validation
* **Run Entire Test Suite:**
  ```bash
  python manage.py test
  ```
* **Run Tests for a Specific App:**
  ```bash
  python manage.py test <app_name>
  ```
* **Django System Check:** (Validates project structure, settings, and models for any errors)
  ```bash
  python manage.py check
  ```

### 📦 Interactive Shell
* **Start Python Interactive Shell inside Django:**
  ```bash
  python manage.py shell
  ```
* **Start Database Interactive CLI:**
  ```bash
  python manage.py dbshell
  ```
