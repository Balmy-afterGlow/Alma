import uuid


def generate_default_nickname() -> str:
    return f"user_{uuid.uuid4().hex[:8]}"
