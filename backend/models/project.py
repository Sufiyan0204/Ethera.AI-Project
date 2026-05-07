from datetime import datetime, timezone


def create_project(title, description, created_by_id):
    """Return a project document dict."""
    return {
        "title": title.strip(),
        "description": description.strip(),
        "created_by": created_by_id,          # ObjectId string
        "members": [created_by_id],           # Creator is always a member
        "created_at": datetime.now(timezone.utc),
    }


def serialize_project(project):
    """Convert a MongoDB project document to a JSON-safe dict."""
    if not project:
        return None
    return {
        "id": str(project["_id"]),
        "title": project["title"],
        "description": project.get("description", ""),
        "created_by": str(project["created_by"]),
        "members": [str(m) for m in project.get("members", [])],
        "created_at": project.get("created_at", "").isoformat() if project.get("created_at") else "",
    }
