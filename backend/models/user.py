from datetime import datetime, timezone

def create_user(name, email, hashed_password, role="Member"):
    """Return a user document dict."""
    return {
        "name": name,
        "email": email.lower().strip(),
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc),
    }


def serialize_user(user):
    """Convert a MongoDB user document to a JSON-safe dict (no password)."""
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user.get("created_at", "").isoformat() if user.get("created_at") else "",
    }
