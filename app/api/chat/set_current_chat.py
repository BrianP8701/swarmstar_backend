from fastapi import FastAPI, Depends, APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.security import validate_token
from app.models import Chat, User

app = FastAPI()
router = APIRouter()


class SetCurrentChatRequest(BaseModel):
    chat_id: str


class SetCurrentChatResponse(BaseModel):
    chat: Chat
    user: User


@router.put("/chat/set_current_chat", response_model=SetCurrentChatResponse)
async def set_current_chat(
    request: SetCurrentChatRequest, user_id: str = Depends(validate_token)
):
    try:
        node_id = request.chat_id

        if not node_id:
            raise HTTPException(status_code=400, detail="Node ID is required")

        try:
            chat = Chat.get_chat(node_id)
        except:
            raise HTTPException(status_code=404, detail="Chat not found")

        user = User.get_user(user_id)
        user.set_current_chat_id(node_id)

        return {"chat": chat, "user": user}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
