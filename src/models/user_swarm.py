from pydantic import BaseModel
from typing import List, Optional, Dict
import copy

from src.database import MongoDBWrapper
from src.models import User
from src.utils.security import generate_uuid

mdb = MongoDBWrapper()

class UserSwarm(BaseModel):
    id: str  # swarm_id
    name: str  # Swarm name
    goal: Optional[str] = None  # Swarm goal
    owner: str  # user_id
    spawned: bool = False
    active: bool = False
    complete: bool = False
    queued_swarm_operations_ids: List[str] = []  # List of swarm_operation_ids
    nodes_with_active_chat: Dict[str, str] = {}  # Dict of node ids to chat names that are active
    nodes_with_terminated_chat: Dict[str, str] = {}  # Dict of node ids to chat names that have terminated their chat

    @classmethod
    def get_user_swarm(cls, swarm_id: str) -> 'UserSwarm':
        return cls(**mdb.get("swarms", swarm_id))

    @classmethod
    def create_empty_user_swarm(cls, user_id: str, name: str):
        user_swarm = cls(
            id=generate_uuid("swarm"),
            name=name,
            owner=user_id
        )
        mdb.insert("swarms", user_swarm.id, user_swarm.model_dump(exclude={'id'}))
        return user_swarm

    def update(self, updated_values: dict):
        mdb.update("swarms", self.id, updated_values)
        for field, value in updated_values.items():
            setattr(self, field, value)

    @classmethod
    def delete_user_swarm(cls, swarm_id: str):
        mdb.delete("swarms", swarm_id)

    def append_queued_swarm_operation(self, swarm_operation_id: str):
        mdb.append("swarms", self.id, {"queued_swarm_operations_ids": swarm_operation_id})
        self.queued_swarm_operations_ids.append(swarm_operation_id)

    def remove_queued_swarm_operation(self, swarm_operation_id: str):
        mdb.remove_from_list("swarms", self.id, {"queued_swarm_operations_ids": swarm_operation_id})
        self.queued_swarm_operations_ids.remove(swarm_operation_id)

    def update_on_spawn(self, goal: str):
        self.update({"goal": goal, "spawned": True, "active": True, "complete": False})

    def deactivate(self):
        self.update({"active": False})

    def activate(self):
        self.update({"active": True})

    def complete(self):
        self.update({"complete": True})

    def pause(self):
        self.update({"active": False})

    def copy_swarm(self, user_id: str, swarm_name: str, old_swarm_id: str):
        try:
            old_swarm = self.get_user_swarm(old_swarm_id)
            swarm_copy = copy.deepcopy(old_swarm)
            swarm_copy.id = generate_uuid("swarm")
            swarm_copy.name = swarm_name

            if swarm_copy.spawned:
                old_swarm_state
                
                
                
                
                duplicate_swarm(old_swarm_id, swarm_copy.id)
                swarm_copy.nodes_with_active_chat = {}
                for chat_id in old_swarm.nodes_with_active_chat.keys():
                    old_chat = get_chat(chat_id)
                    chat = copy.deepcopy(old_chat)
                    chat.id = generate_uuid("chat")
                    swarm_copy.nodes_with_active_chat[chat.id] = old_swarm.nodes_with_active_chat[chat_id]
                    chat.message_ids = []
                    for message_id in old_chat.message_ids:
                        message = get_message(message_id)
                        message.id = generate_uuid("message")
                        chat.message_ids.append(message.id)
                        add_kv(swarmstar_ui_db_name, "messages", message.id, message.model_dump())
                    add_kv(swarmstar_ui_db_name, "chats", chat.id, chat.model_dump())
                
                swarm_copy.nodes_with_terminated_chat = {}
                for chat_id in old_swarm.nodes_with_terminated_chat.keys():
                    old_chat = get_chat(chat_id)
                    chat = copy.deepcopy(old_chat)
                    chat.id = generate_uuid("chat")
                    swarm_copy.nodes_with_terminated_chat[chat.id] = old_swarm.nodes_with_terminated_chat[chat_id]
                    chat.message_ids = []
                    for message_id in old_chat.message_ids:
                        message = get_message(message_id)
                        message.id = generate_uuid("message")
                        chat.message_ids.append(message.id)
                    add_kv(swarmstar_ui_db_name, "chats", chat.id, chat.model_dump())
                
            mdb.insert("swarms", swarm_copy.id, swarm_copy.model_dump())
            user = User.get_user(user_id)
            user.swarm_ids[swarm_copy.id] = swarm_name
            user.current_swarm_id = swarm_copy.id
            User.set_user(user)
            return swarm_copy
        except Exception as e:
            raise e