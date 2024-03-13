from pydantic import BaseModel
from typing import Dict, Optional

from src.database import MongoDBWrapper
from src.models import UserSwarm

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
    def create_new_user(cls, user_profile):
        user = cls(id=user_profile.user_id, swarm_ids={}, username=user_profile.id)
        db.insert("users", user.id, user.model_dump(exclude={'id'}))
        return user

    def update(self, updated_values: dict):
        db.update("users", self.id, updated_values)
        for field, value in updated_values.items():
            setattr(self, field, value)

    def set(self):
        db.set("users", self.id, self.model_dump(exclude={'id'}))

    def set_current_swarm(self, swarm_id: str):
        self.update({"current_swarm_id": swarm_id})
        if swarm_id:
            user_swarm = UserSwarm.get_user_swarm(swarm_id)
            if user_swarm.spawned:
                return UserSwarm.get_current_swarm_state_representation(swarm_id)
            else:
                return None

    def set_current_chat_id(self, node_id: str):
        self.update({"current_chat_id": node_id})

    @classmethod 
    def delete_user(cls, user_id: str):
        user = cls.get_user(user_id)
        username = user.username
        for swarm_id in user.swarm_ids:
            UserSwarm.delete_user_swarm(swarm_id)
        db.delete("users", user_id)
        db.delete("user_profiles", username)
