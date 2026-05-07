# 🚀 Team Task Manager

A full-stack Team Task Manager web application built with **Flask**, **MongoDB**, and **JWT authentication**.

---

## 📋 Features

- 🔐 **JWT Authentication** — Secure signup/login with bcrypt password hashing
- 👥 **Role-Based Access Control** — Admin and Member roles with fine-grained permissions
- 📁 **Project Management** — Create, view, and delete projects; manage members
- ✅ **Task Management** — Assign tasks to team members, track status, highlight overdue tasks
- 📊 **Dashboard** — Overview stats: total tasks, in progress, completed, overdue
- 🌐 **REST API** — Clean, versioned API with proper error handling

---

## 🧱 Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Flask, Flask-JWT-Extended, Flask-CORS |
| Database   | MongoDB (PyMongo / Flask-PyMongo)   |
| Auth       | JWT tokens + bcrypt                 |
| Frontend   | HTML5, CSS3 (custom), Vanilla JS    |

---

## 📁 Folder Structure

```
team-task-manager/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── db.py               # PyMongo instance
│   ├── requirements.txt
│   ├── Procfile            # Railway deployment
│   ├── runtime.txt         # Python version
│   ├── .env                # Environment variables (not committed)
│   ├── models/
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── routes/
│   │   ├── auth.py         # POST /api/auth/signup, /api/auth/login
│   │   ├── projects.py     # /api/projects
│   │   ├── tasks.py        # /api/tasks
│   │   └── users.py        # /api/users
│   └── utils/
│       └── auth_helpers.py # Role decorators
└── frontend/
    ├── index.html          # Signup page
    ├── login.html          # Login page
    ├── dashboard.html      # Dashboard
    ├── projects.html       # Projects management
    ├── tasks.html          # Tasks management
    ├── scripts.js          # Shared JS (API client, auth, toast)
    └── styles.css          # Global dark-themed stylesheet
```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/team-task-manager.git
cd team-task-manager
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env` and fill in your values:

```env
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/teamtaskmanager
JWT_SECRET_KEY=your-super-secret-key
FLASK_ENV=development
PORT=5000
```

### 4. Run the backend

```bash
python app.py
```

The API will be running at `http://localhost:5000`.

### 5. Open the frontend

Open `frontend/index.html` in your browser, or serve it with any static server:

```bash
# Using Python's built-in server from the frontend directory
cd ../frontend
python -m http.server 3000
```

Navigate to `http://localhost:3000`.

> **Note:** If running on different ports, update `API_BASE` in `frontend/scripts.js`.

---

## 🔗 API Endpoints

### Auth

| Method | Endpoint            | Description          | Auth Required |
|--------|---------------------|----------------------|---------------|
| POST   | `/api/auth/signup`  | Register a new user  | No            |
| POST   | `/api/auth/login`   | Login and get token  | No            |

**Signup body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "secret123",
  "role": "Admin"
}
```

**Login body:**
```json
{
  "email": "jane@example.com",
  "password": "secret123"
}
```

---

### Projects

| Method | Endpoint                           | Description              | Role Required |
|--------|------------------------------------|--------------------------|---------------|
| POST   | `/api/projects`                    | Create a project         | Admin         |
| GET    | `/api/projects`                    | List projects            | Any           |
| GET    | `/api/projects/<id>`               | Get single project       | Any           |
| DELETE | `/api/projects/<id>`               | Delete project + tasks   | Admin         |
| POST   | `/api/projects/<id>/members`       | Add a member             | Admin         |
| DELETE | `/api/projects/<id>/members/<uid>` | Remove a member          | Admin         |

---

### Tasks

| Method | Endpoint                    | Description                        | Role Required       |
|--------|-----------------------------|------------------------------------|---------------------|
| POST   | `/api/tasks`                | Create & assign a task             | Admin               |
| GET    | `/api/tasks`                | List tasks (filtered by role)      | Any                 |
| GET    | `/api/tasks/<id>`           | Get single task                    | Any (own task only) |
| PATCH  | `/api/tasks/<id>`           | Update task (status or full edit)  | Any (own task only) |
| DELETE | `/api/tasks/<id>`           | Delete a task                      | Admin               |
| GET    | `/api/tasks/stats/overview` | Dashboard stats                    | Any                 |

---

### Users

| Method | Endpoint           | Description          | Role Required |
|--------|--------------------|----------------------|---------------|
| GET    | `/api/users`       | List all users       | Any           |
| GET    | `/api/users/me`    | Get own profile      | Any           |
| DELETE | `/api/users/<id>`  | Delete a user        | Admin         |

---

## 🔐 Authentication

All protected routes require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

The token is returned on successful signup/login and stored in `localStorage`.

---

## 👥 Role Permissions

| Feature             | Admin | Member        |
|---------------------|-------|---------------|
| Create project      | ✅    | ❌            |
| Delete project      | ✅    | ❌            |
| Add/remove member   | ✅    | ❌            |
| Create/assign task  | ✅    | ❌            |
| View all tasks      | ✅    | ❌ (own only) |
| Update task status  | ✅    | ✅ (own only) |
| Delete task         | ✅    | ❌            |
| View dashboard      | ✅    | ✅            |

---

## 🌐 Deployment (Railway)

### Backend

1. Create a new Railway project
2. Connect your GitHub repository
3. Set the **Root Directory** to `backend/`
4. Add environment variables in Railway dashboard:
   - `MONGO_URI` → your MongoDB Atlas connection string
   - `JWT_SECRET_KEY` → a strong random secret
   - `PORT` → `5000` (Railway sets this automatically)
5. Railway will auto-detect the `Procfile` and deploy

### MongoDB Atlas

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Whitelist Railway's IPs (or `0.0.0.0/0` for simplicity)
3. Create a database user and copy the connection string into `MONGO_URI`

### Frontend

After deploying the backend, update `API_BASE` in `frontend/scripts.js`:

```js
const API_BASE = "https://your-railway-app.up.railway.app/api";
```

Then deploy the `frontend/` directory to:
- **Netlify**: Drag & drop the folder
- **Vercel**: Connect repo and set root to `frontend/`
- **GitHub Pages**: Enable in repo settings

---

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique)",
  "password": "bcrypt hash",
  "role": "Admin | Member",
  "created_at": "datetime"
}
```

### Projects Collection
```json
{
  "_id": "ObjectId",
  "title": "string",
  "description": "string",
  "created_by": "user_id",
  "members": ["user_id"],
  "created_at": "datetime"
}
```

### Tasks Collection
```json
{
  "_id": "ObjectId",
  "title": "string",
  "description": "string",
  "assigned_to": "user_id",
  "project_id": "project_id",
  "status": "Todo | In Progress | Done",
  "due_date": "datetime",
  "created_by": "user_id",
  "created_at": "datetime"
}
```

---

## 🎨 UI Pages

| Page              | File                | Description                            |
|-------------------|---------------------|----------------------------------------|
| Sign Up           | `index.html`        | Register with role selection           |
| Login             | `login.html`        | Authenticate and get token             |
| Dashboard         | `dashboard.html`    | Stats overview + recent tasks/projects |
| Projects          | `projects.html`     | Project CRUD + member management       |
| Tasks             | `tasks.html`        | Task list with filters + status update |

---

## 📦 Demo Video

> Record a 2–5 min demo showing:
> 1. Register as Admin → Login
> 2. Create a project → Add a member
> 3. Create a task → Assign to member
> 4. Member login → Update task status
> 5. Dashboard overview

---

*Built with ❤️ using Flask + MongoDB + JWT*
