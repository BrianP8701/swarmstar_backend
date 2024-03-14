from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import copy

from app.models.chat import BackendChat
from app.models.swarmstar_wrapper import SwarmstarWrapper
from app.database import MongoDBWrapper
from app.models.user import User
from app.utils.security import generate_uuid

db = MongoDBWrapper()
ss = SwarmstarWrapper()

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
        return cls(**db.get("swarms", swarm_id))

    @classmethod
    def create_empty_user_swarm(cls, user_id: str, name: str):
        user_swarm = cls(
            id=generate_uuid("swarm"),
            name=name,
            owner=user_id
        )
        db.insert("swarms", user_swarm.id, user_swarm.model_dump(exclude={'id'}))
        return user_swarm

    @staticmethod
    def update(swarm_id: str, updated_values: dict):
        db.update("swarms", swarm_id, updated_values)

    def update(self, updated_values: dict) -> 'UserSwarm':
        db.update("swarms", self.id, updated_values)
        for field, value in updated_values.items():
            setattr(self, field, value)
        return self

    def append_queued_swarm_operation(self, swarm_operation_id: str):
        db.append("swarms", self.id, {"queued_swarm_operations_ids": swarm_operation_id})
        self.queued_swarm_operations_ids.append(swarm_operation_id)

    def remove_queued_swarm_operation(self, swarm_operation_id: str):
        db.remove_from_list("swarms", self.id, {"queued_swarm_operations_ids": swarm_operation_id})
        self.queued_swarm_operations_ids.remove(swarm_operation_id)

    def add_chat(self, node_id: str, chat_name: str):
        self.nodes_with_active_chat[node_id] = chat_name
        self.update({"nodes_with_active_chat": self.nodes_with_active_chat})

    def update_on_spawn(self, goal: str):
        self.update({"goal": goal, "spawned": True, "active": True, "complete": False})

    def deactivate(self):
        self.update({"active": False})

    def activate(self):
        self.update({"active": True})

    def set_complete(self):
        self.update({"complete": True})

    def pause(self):
        self.update({"active": False})

    def terminate_chat(self, node_id: str):
        chat = BackendChat.get_chat(node_id)
        chat.update({"alive": False})
        self.nodes_with_terminated_chat[node_id] = chat.id
        self.nodes_with_active_chat.pop(node_id)
        self.update({"nodes_with_terminated_chat": self.nodes_with_terminated_chat, "nodes_with_active_chat": self.nodes_with_active_chat})

    @staticmethod
    def get_swarm_tree(swarm_id: str) -> Union[Dict[str, Any], None]:
        if swarm_id:
            user_swarm = UserSwarm.get_user_swarm(swarm_id)
            if user_swarm.spawned:
                return SwarmstarWrapper.get_current_swarm_state_representation(swarm_id)
            else:
                return None

    @staticmethod
    def copy_swarm(user_id: str, swarm_name: str, old_swarm_id: str) -> 'UserSwarm':
        try:
            old_swarm = UserSwarm.get_user_swarm(old_swarm_id)
            swarm_copy = copy.deepcopy(old_swarm)
            swarm_copy.id = generate_uuid("swarm")
            swarm_copy.nodes_with_active_chat = {}
            swarm_copy.nodes_with_terminated_chat = {}
            swarm_copy.name = swarm_name

            if swarm_copy.spawned:
                old_swarm_state = ss.get_swarm_state(old_swarm_id)
                old_swarm_history = ss.get_swarm_history(old_swarm_id)
                
                swarm_state = []
                swarm_history = []
                queued_swarm_operations_ids = []
                nodes_with_active_chat = {}
                nodes_with_terminated_chat = {}
                
                def copy_chat_nodes(node_ids, nodes_with_chat, swarm_state_container):
                    for node_id in node_ids:
                        old_chat = BackendChat.get_chat(node_id)
                        old_node = ss.get_swarm_node(node_id)
                        old_swarm_state.remove(node_id)
                        node = copy.deepcopy(old_node)
                        chat = copy.deepcopy(old_chat)
                        node.id = generate_uuid("node")
                        chat.id = node.id
                        nodes_with_chat[node.id] = node.name
                        swarm_state_container.append(node.id)
                        ss.add_swarm_node(node)
                        db.insert("chats", chat.id, chat.model_dump())

                copy_chat_nodes(old_swarm.nodes_with_active_chat.keys(), nodes_with_active_chat, swarm_state)
                copy_chat_nodes(old_swarm.nodes_with_terminated_chat.keys(), nodes_with_terminated_chat, swarm_state)
                
                for operation_id in old_swarm.queued_swarm_operations_ids:
                    old_operation = ss.get_swarm_operation(operation_id)
                    old_swarm_history.remove(operation_id)
                    operation = copy.deepcopy(old_operation)
                    operation.id = generate_uuid("operation")
                    queued_swarm_operations_ids.append(operation.id)
                    swarm_history.append(operation.id)
                    ss.add_swarm_operation(operation)
                
                for node_id in old_swarm_state:
                    old_node = ss.get_swarm_node(node_id)
                    node = copy.deepcopy(old_node)
                    node.id = generate_uuid("node")
                    swarm_state.append(node.id)
                    ss.add_swarm_node(node)
                
                for operation_id in old_swarm_history:
                    old_operation = ss.get_swarm_operation(operation_id)
                    operation = copy.deepcopy(old_operation)
                    operation.id = generate_uuid("operation")
                    swarm_history.append(operation.id)
                    ss.add_swarm_operation(operation)
                
                swarm_copy.nodes_with_active_chat = nodes_with_active_chat
                swarm_copy.nodes_with_terminated_chat = nodes_with_terminated_chat
                swarm_copy.queued_swarm_operations_ids = queued_swarm_operations_ids

                db.insert("swarm_state", swarm_copy.id, {"data": swarm_state})
                db.insert("swarm_history", swarm_copy.id, {"data": swarm_history})
                
            db.insert("swarms", swarm_copy.id, swarm_copy.model_dump(exclude={'id'}))
            user = User.get_user(user_id)
            user.swarm_ids[swarm_copy.id] = swarm_name
            user.current_swarm_id = swarm_copy.id
            User.set(user_id, {"swarm_ids": user.swarm_ids, "current_swarm_id": user.current_swarm_id})
            return swarm_copy
        except Exception as e:
            raise e

    @classmethod
    def delete_user_swarm(cls, swarm_id: str):
        user_swarm = cls.get_user_swarm(swarm_id)
        
        for node_id in user_swarm.nodes_with_active_chat:
            BackendChat.delete_chat(node_id)
        for node_id in user_swarm.nodes_with_terminated_chat:
            BackendChat.delete_chat(node_id)
        db.delete("swarms", swarm_id)
        
        user = User.get_user(user_swarm.owner)
        del user.swarm_ids[swarm_id]
        if user.current_swarm_id == swarm_id:
            user.current_swarm_id = None
        user.update({"swarm_ids": user.swarm_ids, "current_swarm_id": user.current_swarm_id})
        
        SwarmstarWrapper.delete_swarmstar_space(swarm_id)
