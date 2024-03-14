from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.security import validate_token
from app.models import UserSwarm

router = APIRouter()


class PauseSwarmRequest(BaseModel):
    swarm_id: str


class PauseSwarmResponse(BaseModel):
    swarm: UserSwarm


@router.put("/swarm/pause_swarm", response_model=PauseSwarmResponse)
async def pause_swarm(
    pause_swarm_request: PauseSwarmRequest,
    user_id: str = Depends(validate_token),
):
    try:
        swarm_id = pause_swarm_request.swarm_id
        user_swarm = UserSwarm.get_user_swarm(swarm_id)
        user_swarm.pause()
        return {"swarm": user_swarm}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
