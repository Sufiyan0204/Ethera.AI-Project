from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo
from models.project import create_project, serialize_project
from utils.auth_helpers import admin_required, get_current_user

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("", methods=["POST"])
@admin_required
def create_new_project():
    """Admin: Create a new project."""
    try:
        data = request.get_json()
        if not data or not data.get("title", "").strip():
            return jsonify({"error": "Project 'title' is required"}), 400

        title = data["title"].strip()
        description = data.get("description", "").strip()
        user_id = get_jwt_identity()

        project_doc = create_project(title, description, user_id)
        result = mongo.db.projects.insert_one(project_doc)
        project_doc["_id"] = result.inserted_id

        return jsonify({
            "message": "Project created",
            "project": serialize_project(project_doc),
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("", methods=["GET"])
@jwt_required()
def get_projects():
    """Get projects visible to the current user."""
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if user and user.get("role") == "Admin":
            # Admins see all projects
            projects = list(mongo.db.projects.find())
        else:
            # Members see only projects they are members of
            projects = list(mongo.db.projects.find({"members": user_id}))

        return jsonify([serialize_project(p) for p in projects]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/<project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    """Get a single project by ID."""
    try:
        project = mongo.db.projects.find_one({"_id": ObjectId(project_id)})
        if not project:
            return jsonify({"error": "Project not found"}), 404
        return jsonify(serialize_project(project)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/<project_id>", methods=["DELETE"])
@admin_required
def delete_project(project_id):
    """Admin: Delete a project and its tasks."""
    try:
        project = mongo.db.projects.find_one({"_id": ObjectId(project_id)})
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Remove all tasks belonging to the project
        mongo.db.tasks.delete_many({"project_id": project_id})
        mongo.db.projects.delete_one({"_id": ObjectId(project_id)})

        return jsonify({"message": "Project and its tasks deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/<project_id>/members", methods=["POST"])
@admin_required
def add_member(project_id):
    """Admin: Add a user to a project."""
    try:
        data = request.get_json()
        member_id = data.get("user_id", "").strip()
        if not member_id:
            return jsonify({"error": "user_id is required"}), 400

        # Verify user exists
        if not mongo.db.users.find_one({"_id": ObjectId(member_id)}):
            return jsonify({"error": "User not found"}), 404

        result = mongo.db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$addToSet": {"members": member_id}},
        )
        if result.matched_count == 0:
            return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Member added to project"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/<project_id>/members/<member_id>", methods=["DELETE"])
@admin_required
def remove_member(project_id, member_id):
    """Admin: Remove a user from a project."""
    try:
        result = mongo.db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": member_id}},
        )
        if result.matched_count == 0:
            return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Member removed from project"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
