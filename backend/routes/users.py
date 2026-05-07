from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo
from models.user import serialize_user
from utils.auth_helpers import admin_required

users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["GET"])
@jwt_required()
def get_users():
    """Get all users (for populating dropdowns). All authenticated users can access."""
    try:
        users = list(mongo.db.users.find({}, {"password": 0}))
        return jsonify([serialize_user(u) for u in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """Get the currently authenticated user's profile."""
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(serialize_user(user)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Admin: Delete a user."""
    try:
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
