from swarmstar.models import ActionOperation

from src.server.swarm_operation_queue import swarm_operation_queue
from src.models import BackendChat, SwarmstarWrapper, SwarmMessage

async def swarm_handle_user_message(swarm_id: str, node_id: str, message_id: str):
    chat = BackendChat.get_chat(node_id)
    message = SwarmMessage.get_message(message_id)

    user_communication_operation = chat.user_communication_operation

    return_operation = ActionOperation(
        node_id=chat.id,
        args={**{"user_response": message.content}, **user_communication_operation.context},
        function_to_call=user_communication_operation.next_function_to_call,
    )
    
    SwarmstarWrapper.add_swarm_operation(return_operation)

    chat.update({"user_communication_operation": None})
    swarm_operation_queue.put_nowait((swarm_id, return_operation))
