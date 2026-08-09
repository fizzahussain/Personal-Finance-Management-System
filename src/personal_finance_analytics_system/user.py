from dataclasses import dataclass


@dataclass
class User:
    """Represent an application user"""

    email: str
    password_hash: str
    user_id: int | None = None