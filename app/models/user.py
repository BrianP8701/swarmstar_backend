from pydantic import BaseModel
from typing import Dict, Optional, Any

from app.database import MongoDBWrapper
from app.models.user_profile import UserProfile

db = MongoDBWrapper()

class User(BaseModel):
    id: str  # user_id
    swarm_ids: Dict[str, str]
    current_swarm_id: Optional[str] = None
    current_chat_id: Optional[str] = None
    current_node_id: Optional[str] = None

    @classmethod
    def get(cls, user_id: str):
        user = db.get("users", user_id)
        return cls(**user)

    @classmethod
    def create_new_user(cls, user_profile: UserProfile):
        user = cls(id=user_profile.user_id, swarm_ids={}, username=user_profile.id)
        db.insert("users", user.id, user.model_dump(exclude={'id'}))
        return user

    def update(self, updated_values: dict):
        db.update("users", self.id, updated_values)

    def replace(self, updated_values: dict):
        db.replace("users", self.id, updated_values)

    def set_current_swarm(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        user = User.get(self.id)
        user.update({"current_swarm_id": swarm_id})

    def set_current_chat_id(self, node_id: str):
        self.update({"current_chat_id": node_id})

    def add_swarm(self, swarm_id: str, swarm_name: str):
        user = User.get(self.id)
        user.swarm_ids[swarm_id] = swarm_name
        db.update("users", self.id, {"swarm_ids": user.swarm_ids})
