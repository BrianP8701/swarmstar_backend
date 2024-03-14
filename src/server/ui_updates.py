"""
These are UI updates that are pushed from the swarm to the user's UI.
"""
import asyncio

from swarmstar.models import SwarmOperation

from src.models import User, UserSwarm, SwarmOperation, SwarmMessage, SwarmstarWrapper
from src.server.websocket_manager import manager


def is_user_online(user_id: str) -> bool:
    return manager.is_connected(user_id)

def is_user_in_swarm(user_id: str, swarm_id: str) -> bool:
    return User.get_user(user_id).current_swarm_id == swarm_id

def is_user_in_chat(user_id: str, chat_id: str) -> bool:
    return User.get_user(user_id).current_chat_id == chat_id

def send_swarm_update_to_ui(swarm_id: str) -> None:
    """
    After any change to the UserSwarm, send the updated UserSwarm to the UI.
    """
    try:
        user_swarm = UserSwarm.get_user_swarm(swarm_id)
        user_id = user_swarm.owner
        asyncio.create_task(
            manager.send_personal_message(
                {
                    "type": "update_swarm",
                    "data": {"swarm": user_swarm.model_dump()},
                },
                user_id,
            )
        )
    except Exception as e:
        raise e

def append_message_to_chat_in_ui(swarm_id: str, message_id: str) -> None:
    """
    After an ai message is created, append it to the chat in the UI.
    """
    try:
        user_id = UserSwarm.get_user_swarm(swarm_id).owner
        asyncio.create_task(
            manager.send_personal_message(
                {
                    "type": "append_message_to_chat",
                    "data": {"message": SwarmMessage.get_message(message_id).model_dump()},
                },
                user_id,
            )
        )
    except Exception as e:
        raise e

def add_new_nodes_to_tree_in_ui(swarm_id: str, spawn_operation_id: str) -> None:
    """
    After a spawn operation, add the new node to the tree in the UI.
    """
    try:
        spawn_operation = SwarmstarWrapper.get_swarm_operation(spawn_operation_id)
        user_id = UserSwarm.get_user_swarm(swarm_id).owner
        swarm_config = UserSwarm.get_user_swarm(swarm_id).swarm_config
        
        parent_id = spawn_operation.parent_node_id
        spawned_node = SwarmstarWrapper.get_swarm_node(spawn_operation.node_id)

        add_node_payload = {
            "parent_node_id" : parent_id,
            "new_node": {
                "name": spawned_node.name,
                "attributes": {
                    "directive": spawned_node.message,
                    "node_id": spawned_node.id,
                    "status": "active"
                }
            }
        }
        asyncio.create_task(
            manager.send_personal_message(
                {
                    "type": "add_node_to_tree",
                    "data": add_node_payload,
                },
                user_id
            )
        )
    except Exception as e:
        raise e


def update_node_status_in_ui(swarm_id: str, operation_id: str) -> None:
    try:
        operation = SwarmstarWrapper.get_swarm_operation(operation_id)
        user_id = UserSwarm.get_user_swarm(swarm_id).owner
        operation_type = operation.operation_type
        if operation_type == "spawn":
            node_id = operation.parent_node_id
        else:
            node_id = operation.node_id
        
        if operation_type == "spawn":
            asyncio.create_task(
                manager.send_personal_message(
                    {
                        "type": "update_node_status",
                        "data": {"node_id": node_id, "status": "waiting"},
                    },
                    user_id,
                )
            )
        elif operation_type == "terminate":
            node = SwarmstarWrapper.get_swarm_node(node_id)
            if not node.alive:
                asyncio.create_task(
                    manager.send_personal_message(
                        {
                            "type": "update_node_status",
                            "data": {"node_id": node_id, "status": "terminated"},
                        },
                        user_id
                    )
                )
    except Exception as e:
        raise e
