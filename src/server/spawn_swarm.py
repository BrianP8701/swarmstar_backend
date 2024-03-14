"""
This module is responsible for spawning a new swarm 
when the user presses the spawn button in the UI.
"""
import os

from swarmstar import spawn_swarm as swarmstar_spawn_swarm
from swarmstar.models import SwarmOperation

from src.server.swarm_operation_queue import swarm_operation_queue
from src.models import UserSwarm, SwarmstarWrapper

async def spawn_swarm(swarm_id: str, goal: str):
    """
    This is called when the user presses the spawn button
    """
    try:
        swarm_config = SwarmstarWrapper.get_swarm_config("default_config")
        root_path = find_empty_swarm_folder()
        swarm_config.id = swarm_id
        swarm_config.root_path = root_path
        
        root_swarm_operation = swarmstar_spawn_swarm(swarm_config, goal)
        swarm_operation_queue.put_nowait((swarm_id, root_swarm_operation))
    except Exception as e:
        print(e)

def resume_swarm(swarm_id: str):
    """
    This is called when the user presses the resume button
    """
    try:
        user_swarm = UserSwarm.get_user_swarm(swarm_id)
        for operation in user_swarm.queued_swarm_operations_ids:
            operation = SwarmstarWrapper.get_swarm_operation(operation)
            swarm_operation_queue.put_nowait((swarm_id, operation))
        user_swarm.update({"queued_swarm_operations_ids": [], "active": True})
    except Exception as e:
        print(e)

def find_empty_swarm_folder() -> str:
    base_path = "my_swarms"
    index = 0
    while True:
        folder_path = os.path.join(base_path, f"swarm_{index}")
        if not os.path.exists(folder_path):
            return folder_path
        index += 1
