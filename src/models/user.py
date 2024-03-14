from pydantic import BaseModel
from typing import Dict, Optional, Any

from src.database import MongoDBWrapper
from src.models.user_profile import UserProfile

db = MongoDBWrapper()

class User(BaseModel):
    id: str  # user_id
    swarm_ids: Dict[str, str]
    current_swarm_id: Optional[str] = None
    current_chat_id: Optional[str] = None
    current_node_id: Optional[str] = None
    username: str

    @classmethod
    def get_user(cls, user_id: str):
        return cls(**db.get("users", user_id))

    @classmethod
    def create_new_user(cls, user_profile: UserProfile):
        user = cls(id=user_profile.user_id, swarm_ids={}, username=user_profile.id)
        db.insert("users", user.id, user.model_dump(exclude={'id'}))
        return user

    @staticmethod
    def update(user_id: str, updated_values: dict):
        db.update("users", user_id, updated_values)

    def update(self, updated_values: dict):
        db.update("users", self.id, updated_values)
        for field, value in updated_values.items():
            setattr(self, field, value)
        return self
    
    @staticmethod
    def set(user_id, updated_values: dict):
        db.set("users", user_id, updated_values)

    def set_current_swarm(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        self.update({"current_swarm_id": swarm_id})

    def set_current_chat_id(self, node_id: str):
        self.update({"current_chat_id": node_id})
