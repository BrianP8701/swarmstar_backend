from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import copy

from app.models.chat import BackendChat, SwarmMessage
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
        db.append("swarms", self.id, "queued_swarm_operations_ids", swarm_operation_id)
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
        self.nodes_with_terminated_chat[node_id] = self.nodes_with_active_chat[node_id]
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
            swarm_copy.name = swarm_name

            if swarm_copy.spawned:
                old_swarm_state = ss.get_swarm_state(old_swarm_id)
                old_swarm_history = ss.get_swarm_history(old_swarm_id)

                old_nodes_with_active_chat = old_swarm.nodes_with_active_chat
                old_nodes_with_terminated_chat = old_swarm.nodes_with_terminated_chat

                swarm_state = []
                swarm_history = []
                queued_swarm_operations_ids = []
                nodes_with_active_chat = {}
                nodes_with_terminated_chat = {}

                old_node_ids_to_new_node_ids = {}
                old_operation_ids_to_new_operation_ids = {}

                for old_node_id in old_swarm_state:
                    old_node_ids_to_new_node_ids[old_node_id] = generate_uuid("node")
                for old_operation_id in old_swarm_history:
                    old_operation_ids_to_new_operation_ids[old_operation_id] = generate_uuid("operation")

                for old_operation_id in old_swarm.queued_swarm_operations_ids:
                    old_operation_ids_to_new_operation_ids[old_operation_id] = generate_uuid("operation")
                    queued_swarm_operations_ids.append(old_operation_ids_to_new_operation_ids[old_operation_id])
                    operation = ss.get_swarm_operation(old_operation_id)
                    operation.id = old_operation_ids_to_new_operation_ids[old_operation_id]
                    if operation.node_id:
                        operation.node_id = old_node_ids_to_new_node_ids[operation.node_id]
                    if operation.operation_type == "spawn":
                        if operation.parent_node_id:
                            operation.parent_node_id = old_node_ids_to_new_node_ids[operation.parent_node_id]
                    elif operation.operation_type == "terminate":
                        operation.terminator_node_id = old_node_ids_to_new_node_ids[operation.terminator_node_id]
                    ss.add_swarm_operation(operation)

                for old_node_id in old_swarm_state:
                    old_node = ss.get_swarm_node(old_node_id)
                    node = copy.deepcopy(old_node)
                    node.id = old_node_ids_to_new_node_ids[old_node_id]
                    new_children_ids = []
                    for child_id in node.children_ids:
                        new_children_ids.append(old_node_ids_to_new_node_ids[child_id])
                    node.children_ids = new_children_ids
                    if node.parent_id:
                        node.parent_id = old_node_ids_to_new_node_ids[node.parent_id]
                    swarm_state.append(node.id)
                    ss.add_swarm_node(node)
                for old_operation_id in old_swarm_history:
                    old_operation = ss.get_swarm_operation(old_operation_id)
                    operation = copy.deepcopy(old_operation)
                    operation.id = old_operation_ids_to_new_operation_ids[old_operation_id]
                    if operation.node_id:
                        operation.node_id = old_node_ids_to_new_node_ids[operation.node_id]
                    if operation.operation_type == "spawn":
                        if operation.parent_node_id:
                            operation.parent_node_id = old_node_ids_to_new_node_ids[operation.parent_node_id]
                    elif operation.operation_type == "terminate":
                        operation.terminator_node_id = old_node_ids_to_new_node_ids[operation.terminator_node_id]
                    swarm_history.append(operation.id)
                    ss.add_swarm_operation(operation)

                def copy_chats(old_node_ids_to_names: Dict[str, str], new_node_ids_to_names: Dict[str, str]):
                    for old_node_id in old_node_ids_to_names.keys():
                        old_chat = BackendChat.get_chat(old_node_id)
                        chat = copy.deepcopy(old_chat)
                        chat.id = old_node_ids_to_new_node_ids[old_node_id]
                        new_node_ids_to_names[chat.id] = old_node_ids_to_names[old_node_id]
                        chat.message_ids = []
                        for old_message_id in old_chat.message_ids:
                            old_message = SwarmMessage.get_message(old_message_id)
                            message = copy.deepcopy(old_message)
                            message.id = generate_uuid("message")
                            message.create()
                            chat.message_ids.append(message.id)
                        if chat.user_communication_operation:
                            new_user_comm_op_id = generate_uuid("operation")
                            chat.user_communication_operation.id = new_user_comm_op_id
                            chat.user_communication_operation.node_id = old_node_ids_to_new_node_ids[chat.user_communication_operation.node_id]
                        db.insert("chats", chat.id, chat.model_dump())

                copy_chats(old_nodes_with_active_chat, nodes_with_active_chat)
                copy_chats(old_nodes_with_terminated_chat, nodes_with_terminated_chat)
                
                swarm_copy.nodes_with_active_chat = nodes_with_active_chat
                swarm_copy.nodes_with_terminated_chat = nodes_with_terminated_chat
                swarm_copy.queued_swarm_operations_ids = queued_swarm_operations_ids

                SwarmstarWrapper.add_swarm_state(swarm_copy.id, swarm_state)
                SwarmstarWrapper.add_swarm_history(swarm_copy.id, swarm_history)
                
                old_swarm_config = ss.get_swarm_config(old_swarm_id)
                old_swarm_config.id = swarm_copy.id
                SwarmstarWrapper.add_swarm_config(old_swarm_config)

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
