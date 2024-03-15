"""
The swarm operation queue processes swarm operations of
active swarms.

When transitioning to a cloud-based backend, we'll
replace this with a message queue.
"""
import asyncio

from swarmstar.models import SwarmOperation
from swarmstar import Swarmstar

from app.core.communication.handle_swarm_message import handle_swarm_message
from app.models import UserSwarm, SwarmstarWrapper
from app.database import MongoDBWrapper
from app.core.ui_updates import (
    send_swarm_update_to_ui,
    update_node_status_in_ui,
    is_user_online,
    is_user_in_swarm,
    is_user_in_chat,
    append_message_to_chat_in_ui,
    add_new_nodes_to_tree_in_ui
    )

swarm_operation_queue = asyncio.Queue()
db = MongoDBWrapper()

async def swarm_operation_queue_worker():
    """
    Execute any swarm operations that are queued up.
    Queue the operation if the swarm is inactive.
    """
    while True:
        try:
            swarm_id, operation = await swarm_operation_queue.get()
            swarm = UserSwarm.get_user_swarm(swarm_id)
            if swarm.active:
                asyncio.create_task(
                    execute_swarm_operation(swarm_id, operation)
                )
            else:
                swarm.append_queued_swarm_operation(operation.id)
                swarm_operation_queue.task_done()
        except Exception as e:
            print(f"\n\n\n Error in swarm_operation_queue_worker:\n{e}\n\n\n")
            swarm_operation_queue.task_done()
            continue


async def execute_swarm_operation(swarm_id: str, operation: SwarmOperation):
    """
    Some blocking operations need custom handling in the backend.
    This function will appropriately handle swarm operations.
    """
    try:
        print(f"Executing swarm operation: {operation.id}")
        if operation.operation_type == "user_communication":
            handle_swarm_message(swarm_id, operation)
        else:
            swarm_config = SwarmstarWrapper.get_swarm_config(swarm_id)
            swarmstar = Swarmstar(swarm_config)
            next_operations = await swarmstar.execute(operation)
            if next_operations:
                for next_operation in next_operations:
                    swarm_operation_queue.put_nowait((swarm_id, next_operation))
        
        update_ui_after_swarm_operation(swarm_id, operation.id)
        
    except Exception as e:
        print(f"\n\n\nError in execute_swarm_operation:\n{e}\n\n\n")
        raise e
    finally:
        swarm_operation_queue.task_done()


def update_ui_after_swarm_operation(swarm_id: str, operation_id: str) -> None:
    """
    Call this after executing a swarm operation to update the UI
    in real time if the user is using the interface.
    """
    try:
        swarm_operation = SwarmstarWrapper.get_swarm_operation(operation_id)
        user_id = UserSwarm.get_user_swarm(swarm_id).owner
        swarm_operation_type = swarm_operation.operation_type

        if swarm_operation_type == "terminate":
            if db.exists("chats", swarm_operation.node_id):
                user_swarm = UserSwarm.get_user_swarm(swarm_id)
                user_swarm.terminate_chat(swarm_operation.node_id)

        if is_user_online(user_id):
            if is_user_in_swarm(user_id, swarm_id):                
                update_node_status_in_ui(swarm_id, swarm_operation.id)
                send_swarm_update_to_ui(swarm_id)
                if swarm_operation_type == "user_communication" and is_user_in_chat(user_id, swarm_operation.node_id):
                    append_message_to_chat_in_ui(swarm_id, swarm_operation.message_id)
                elif swarm_operation_type == "spawn" and is_user_in_swarm(user_id, swarm_id):
                    add_new_nodes_to_tree_in_ui(swarm_id, swarm_operation.id)
    except Exception as e:
        raise e
