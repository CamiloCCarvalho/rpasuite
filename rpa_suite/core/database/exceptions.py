# rpa_suite/core/database/exceptions.py


class DatabaseError(Exception):
    """Custom exception for Database errors."""

    def __init__(self, message: str):
        if not message:
            message = "Generic error raised!"
        clean_message = message.replace("DatabaseError:", "").strip()
        super().__init__(f"DatabaseError: {clean_message}")
