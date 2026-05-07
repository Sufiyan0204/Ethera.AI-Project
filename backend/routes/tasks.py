from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from db import mongo
from models.task import create_task, serialize_task, VALID_STATUSES
from utils.auth_helpers import admin_required, get_current_user

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["POST"])
@admin_required
def create_new_task():
    """Admin: Create a task and assign it to a user."""
    try:
        data = request.get_json()

        required = ["title", "assigned_to", "project_id", "due_date"]
        for field in required:
            if not data or not data.get(field, ""):
                return jsonify({"error": f"'{field}' is required"}), 400

        title = data["title"].strip()
        description = data.get("description", "").strip()
        assigned_to = data["assigned_to"].strip()
        project_id = data["project_id"].strip()
        due_date_str = data["due_date"].strip()

        # Validate assigned user exists
        if not mongo.db.users.find_one({"_id": ObjectId(assigned_to)}):
            return jsonify({"error": "Assigned user not found"}), 404

        # Validate project exists
        project = mongo.db.projects.find_one({"_id": ObjectId(project_id)})
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Parse due_date (expect ISO format: YYYY-MM-DD or full ISO)
        try:
            due_date = datetime.fromisoformat(due_date_str).replace(tzinfo=timezone.utc)
        except ValueError:
            return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

        user_id = get_jwt_identity()
        task_doc = create_task(title, description, assigned_to, project_id, due_date, user_id)
        result = mongo.db.tasks.insert_one(task_doc)
        task_doc["_id"] = result.inserted_id

        return jsonify({
            "message": "Task created",
            "task": serialize_task(task_doc),
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def get_tasks():
    """Get tasks based on user role (with optional project_id filter)."""
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        project_id = request.args.get("project_id")

        query = {}
        if project_id:
            query["project_id"] = project_id

        if user and user.get("role") == "Admin":
            tasks = list(mongo.db.tasks.find(query))
        else:
            query["assigned_to"] = user_id
            tasks = list(mongo.db.tasks.find(query))

        return jsonify([serialize_task(t) for t in tasks]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/<task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    """Get a single task by ID."""
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Members can only view their own tasks
        if user.get("role") == "Member" and str(task.get("assigned_to")) != user_id:
            return jsonify({"error": "Access denied"}), 403

        return jsonify(serialize_task(task)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/<task_id>", methods=["PATCH"])
@jwt_required()
def update_task_status(task_id):
    """Members can update their own task status. Admins can update any task."""
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        data = request.get_json()

        task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Members can only update their own tasks
        if user.get("role") == "Member" and str(task.get("assigned_to")) != user_id:
            return jsonify({"error": "You can only update your own tasks"}), 403

        update_fields = {}

        if "status" in data:
            if data["status"] not in VALID_STATUSES:
                return jsonify({"error": f"Status must be one of: {', '.join(VALID_STATUSES)}"}), 400
            update_fields["status"] = data["status"]

        # Admins can also update title, description, due_date, assigned_to
        if user.get("role") == "Admin":
            for field in ["title", "description", "due_date", "assigned_to"]:
                if field in data:
                    if field == "due_date":
                        try:
                            update_fields[field] = datetime.fromisoformat(data[field]).replace(tzinfo=timezone.utc)
                        except ValueError:
                            return jsonify({"error": "Invalid due_date format"}), 400
                    else:
                        update_fields[field] = data[field]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update_fields})
        updated_task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

        return jsonify({
            "message": "Task updated",
            "task": serialize_task(updated_task),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/<task_id>", methods=["DELETE"])
@admin_required
def delete_task(task_id):
    """Admin: Delete a task."""
    try:
        result = mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"message": "Task deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/stats/overview", methods=["GET"])
@jwt_required()
def get_stats():
    """Dashboard stats for the current user."""
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if user and user.get("role") == "Admin":
            all_tasks = list(mongo.db.tasks.find())
            all_projects = list(mongo.db.projects.find())
            total_members = mongo.db.users.count_documents({})
        else:
            all_tasks = list(mongo.db.tasks.find({"assigned_to": user_id}))
            all_projects = list(mongo.db.projects.find({"members": user_id}))
            total_members = None

        from models.task import is_overdue
        now = datetime.now(timezone.utc)

        stats = {
            "total_tasks": len(all_tasks),
            "todo": sum(1 for t in all_tasks if t.get("status") == "Todo"),
            "in_progress": sum(1 for t in all_tasks if t.get("status") == "In Progress"),
            "done": sum(1 for t in all_tasks if t.get("status") == "Done"),
            "overdue": sum(1 for t in all_tasks if is_overdue(t)),
            "total_projects": len(all_projects),
        }
        if total_members is not None:
            stats["total_members"] = total_members

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
