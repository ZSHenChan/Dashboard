from dataclasses import dataclass

@dataclass
class UserContext:
    memory_user_id: str
    chat_id: str