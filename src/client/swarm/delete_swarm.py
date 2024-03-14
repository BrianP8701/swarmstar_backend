from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
import traceback

from src.utils.security import validate_token
from src.models import UserSwarm, User

router = APIRouter()


class SwarmDeleteRequest(BaseModel):
    swarm_id: str


class SwarmDeleteResponse(BaseModel):
    swarm: None
    user: User


@router.delete("/swarm/delete_swarm/{swarm_id}", response_model=SwarmDeleteResponse)
async def delete_swarm(
    swarm_id: str, user_id: str = Depends(validate_token)
):
    try:
        UserSwarm.delete_user_swarm(swarm_id)

        return {"user": User.get_user(user_id), "swarm": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
