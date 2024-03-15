from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

from app.core.communication.handle_user_message import swarm_handle_user_message
from app.utils.security import validate_token
from app.models import Chat, User

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class UserMessageRequest(BaseModel):
    chat_id: str
    message: Message


class UserMessageResponse(BaseModel):
    chat: Chat


@router.put("/chat/handle_user_message")
async def handle_user_message(
    user_message_request: UserMessageRequest,
    user_id: str = Depends(validate_token),
):
    try:
        chat_id = user_message_request.chat_id
        message = user_message_request.message.model_dump()

        if not chat_id or not message:
            raise HTTPException(
                status_code=400, detail="Chat ID and message is required"
            )

        user = User.get_user(user_id)
        
        asyncio.create_task(
            swarm_handle_user_message(user.current_swarm_id, chat_id, message)
        )

        return {"chat": Chat.get_chat(chat_id)}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
