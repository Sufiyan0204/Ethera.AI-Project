from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from bson import ObjectId
from db import mongo


def admin_required(fn):
    """Decorator: only allow Admin role users."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user or user.get("role") != "Admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def member_required(fn):
    """Decorator: allow any authenticated user (Admin or Member)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Return the current authenticated user document from MongoDB."""
    user_id = get_jwt_identity()
    return mongo.db.users.find_one({"_id": ObjectId(user_id)})
