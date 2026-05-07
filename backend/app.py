import os
from flask import Flask, render_template, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from db import mongo

# Load environment variables
load_dotenv()

# Configure paths for frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

def create_app():
    app = Flask(__name__, 
                static_folder=FRONTEND_DIR,
                static_url_path='',
                template_folder=FRONTEND_DIR)

    # Configuration
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/teamtaskmanager")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Tokens don't expire (simplify for MVP)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    mongo.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Serve static files (CSS, JS, images, etc.)
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    # Serve frontend pages
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/projects')
    def projects():
        return render_template('projects.html')

    @app.route('/tasks')
    def tasks():
        return render_template('tasks.html')

    # Catch-all route for SPA navigation (serve index.html for any undefined routes)
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('index.html')

    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Team Task Manager API is running"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")
