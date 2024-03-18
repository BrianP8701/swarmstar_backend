from swarmstar.models import UserCommunicationOperation, SwarmHistory

from app.models import SwarmMessage, BackendChat, UserSwarm
from app.database import MongoDBWrapper

db = MongoDBWrapper()

def handle_swarm_message(
    swarm_id: str, user_comm_operation: UserCommunicationOperation
):
    try:
        node_id = user_comm_operation.node_id

        if not db.exists("chats", node_id):
            chat = BackendChat.create_empty_chat(user_comm_operation.node_id)
            chat_name = user_comm_operation.context["chat_name"]
            user_swarm = UserSwarm.get(swarm_id)
            user_swarm.add_chat(node_id, chat_name)

        message: str = user_comm_operation.message
        message = SwarmMessage(role="ai", content=message)
        message.save()
        chat = BackendChat.get(node_id)
        chat.append_message(message.id)
        chat.update({"user_communication_operation": user_comm_operation.model_dump()})

        SwarmHistory.append(
            swarm_id, 
            user_comm_operation.id
        )

    except Exception as e:
        print('Error in handle_swarm_message:\n', e)
        raise e
