from swarmstar.models import UserCommunicationOperation

from src.models import SwarmMessage, BackendChat, SwarmstarWrapper
from src.database import MongoDBWrapper

db = MongoDBWrapper()

def handle_swarm_message(
    swarm_id: str, user_comm_operation: UserCommunicationOperation
):
    try:
        node_id = user_comm_operation.node_id

        if not db.exists("chats", node_id):
            chat = BackendChat.create_empty_chat(user_comm_operation.node_id)

        message: str = user_comm_operation.message
        message = SwarmMessage(role="ai", content=message)
        SwarmMessage.create(node_id, message)
        chat.update({"user_communication_operation": user_comm_operation.model_dump()})
        
        SwarmstarWrapper.add_swarm_operation_id_to_swarm_history(
            swarm_id, 
            user_comm_operation.id
        )
                
    except Exception as e:
        print('Error in handle_swarm_message:\n', e)
        raise e
