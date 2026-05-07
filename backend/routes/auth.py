import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db import mongo
from models.user import create_user, serialize_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user."""
    try:
        data = request.get_json()

        # Validate required fields
        required = ["name", "email", "password"]
        for field in required:
            if not data or not data.get(field, "").strip():
                return jsonify({"error": f"'{field}' is required"}), 400

        name = data["name"].strip()
        email = data["email"].lower().strip()
        password = data["password"].strip()
        role = data.get("role", "Member")

        if role not in ("Admin", "Member"):
            return jsonify({"error": "Role must be 'Admin' or 'Member'"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # Check duplicate email
        if mongo.db.users.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 409

        # Hash password
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        user_doc = create_user(name, email, hashed, role)
        result = mongo.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        token = create_access_token(identity=str(result.inserted_id))

        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": serialize_user(user_doc),
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()

        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        email = data["email"].lower().strip()
        password = data["password"].strip()

        user = mongo.db.users.find_one({"email": email})
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=str(user["_id"]))

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": serialize_user(user),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
