from fastapi import Depends, APIRouter, HTTPException, Query
from typing import Dict
from pydantic import BaseModel

from app.utils.security import validate_token
from app.models import UserSwarm

router = APIRouter()


class UpdateSwarmRequest(BaseModel):
    swarm_id: str
    swarm_updates: Dict


class UpdateSwarmResponse(BaseModel):
    swarm: UserSwarm


@router.put("/swarm/update_swarm", response_model=UpdateSwarmResponse)
async def update_swarm(
    update_swarm_request: UpdateSwarmRequest, user_id: str = Depends(validate_token)
):
    try:
        swarm_id = update_swarm_request.swarm_id
        swarm_updates = update_swarm_request.swarm_updates

        if not swarm_updates or not swarm_id:
            raise HTTPException(
                status_code=400, detail="Swarm updates and swarm_id is required"
            )

        user_swarm = UserSwarm.get(swarm_id)
        user_swarm.update(swarm_updates)
        return {"swarm": user_swarm}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
