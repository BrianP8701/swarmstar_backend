from typing import Dict

from swarmstar.models import ActionOperation, SwarmOperation

from app.core.swarm_operation_queue import swarm_operation_queue
from app.models import BackendChat, SwarmMessage
from app.core.ui_updates import append_message_to_chat_in_ui

async def swarm_handle_user_message(swarm_id: str, node_id: str, message: Dict[str, str]):
    message = SwarmMessage(**message)
    message.save()
    backend_chat = BackendChat.get(node_id)
    backend_chat.append_message(message.id)
    user_communication_operation = backend_chat.user_communication_operation
    context = user_communication_operation.context
    context.pop("chat_name", None)
    append_message_to_chat_in_ui(swarm_id, message.id)
    
    return_operation = ActionOperation(
        node_id=backend_chat.id,
        args={**{"user_response": message.content}, **context},
        function_to_call=user_communication_operation.next_function_to_call,
    )

    SwarmOperation.save(return_operation)

    backend_chat.update({"user_communication_operation": None})
    swarm_operation_queue.put_nowait((swarm_id, return_operation))
