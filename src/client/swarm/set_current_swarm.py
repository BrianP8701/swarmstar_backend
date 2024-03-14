from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import traceback

from src.utils.security import validate_token
from src.models import UserSwarm, User

router = APIRouter()


class SetCurrentSwarmRequest(BaseModel):
    swarm_id: Optional[str] = None


class SetCurrentSwarmResponse(BaseModel):
    swarm: Optional[UserSwarm] = None
    user: User
    swarm_tree: Optional[dict] = None


@router.put("/swarm/set_current_swarm", response_model=SetCurrentSwarmResponse)
async def set_current_swarm(
    set_current_swarm_request: SetCurrentSwarmRequest,
    user_id: str = Depends(validate_token),
):
    try:
        swarm_id = set_current_swarm_request.swarm_id
        user = User.get_user(user_id)
        user.set_current_swarm(swarm_id)
        swarm_tree = UserSwarm.get_swarm_tree(swarm_id)

        if not swarm_id:
            return {"swarm": None, "user": User.get_user(user_id), "swarm_tree": None}

        return {
            "swarm": UserSwarm.get_user_swarm(swarm_id), 
            "user": User.get_user(user_id), 
            "swarm_tree": swarm_tree
        }

    except Exception as e:
        traceback.print_tb(e.__traceback__)

        print(e)
        raise HTTPException(status_code=500, detail=str(e))
