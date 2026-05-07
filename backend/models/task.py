from datetime import datetime, timezone


VALID_STATUSES = {"Todo", "In Progress", "Done"}


def create_task(title, description, assigned_to_id, project_id, due_date, created_by_id):
    """Return a task document dict."""
    return {
        "title": title.strip(),
        "description": description.strip(),
        "assigned_to": assigned_to_id,        # ObjectId string
        "project_id": project_id,             # ObjectId string
        "status": "Todo",
        "due_date": due_date,                 # datetime object (UTC)
        "created_by": created_by_id,
        "created_at": datetime.now(timezone.utc),
    }


def is_overdue(task):
    """Return True if the task is past its due date and not Done."""
    if task.get("status") == "Done":
        return False
    due = task.get("due_date")
    if not due:
        return False
    # due_date stored as datetime in MongoDB; compare with now UTC
    if due.tzinfo is None:
        due = due.replace(tzinfo=timezone.utc)
    return due < datetime.now(timezone.utc)


def serialize_task(task):
    """Convert a MongoDB task document to a JSON-safe dict."""
    if not task:
        return None
    due = task.get("due_date")
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description", ""),
        "assigned_to": str(task["assigned_to"]) if task.get("assigned_to") else None,
        "project_id": str(task["project_id"]) if task.get("project_id") else None,
        "status": task.get("status", "Todo"),
        "due_date": due.isoformat() if due else None,
        "overdue": is_overdue(task),
        "created_by": str(task["created_by"]) if task.get("created_by") else None,
        "created_at": task.get("created_at", "").isoformat() if task.get("created_at") else "",
    }
