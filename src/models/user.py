from pydantic import BaseModel
from typing import Dict, Optional, Any

from src.database import MongoDBWrapper
from src.models.user_profile import UserProfile
from src.models.user_swarm import UserSwarm
from src.models.swarmstar_wrapper import SwarmstarWrapper

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
        if swarm_id:
            user_swarm = UserSwarm.get_user_swarm(swarm_id)
            if user_swarm.spawned:
                return SwarmstarWrapper.get_current_swarm_state_representation(swarm_id)
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
