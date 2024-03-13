from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from src.utils.security import validate_token
from src.utils.database import get_user_swarm
from src.utils.database import pause_swarm as server_pause_swarm
from src.types import UserSwarm

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
        server_pause_swarm(swarm_id)
        return {"swarm": get_user_swarm(swarm_id)}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
