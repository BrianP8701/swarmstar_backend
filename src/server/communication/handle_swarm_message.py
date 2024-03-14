from swarmstar.models import UserCommunicationOperation
from swarmstar.utils.swarmstar_space import add_swarm_operation_id_to_swarm_history

from src.utils.database import (
    does_chat_exist,
    create_empty_chat,
    create_swarm_message,
    update_chat,
    get_swarm_config
)
from src.types import SwarmMessage


def handle_swarm_message(
    swarm_id: str, user_comm_operation: UserCommunicationOperation
):
    try:
        node_id = user_comm_operation.node_id

        if not does_chat_exist(node_id):
            create_empty_chat(swarm_id, user_comm_operation.node_id)

        message: str = user_comm_operation.message
        message = SwarmMessage(role="ai", content=message)
        create_swarm_message(node_id, message)
        update_chat(node_id, {"user_communication_operation": user_comm_operation.model_dump()})
        
        add_swarm_operation_id_to_swarm_history(
            get_swarm_config(swarm_id), 
            user_comm_operation.id
        )
                
    except Exception as e:
        print('Error in handle_swarm_message:\n', e)
        raise e
