from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

from app.core.spawn_swarm import spawn_swarm as _spawn_swarm
from app.utils.security import validate_token
from app.models import UserSwarm

router = APIRouter()


class SpawnSwarmRequest(BaseModel):
    swarm_id: str
    goal: str


class SpawnSwarmResponse(BaseModel):
    swarm: UserSwarm


@router.put("/swarm/spawn_swarm", response_model=SpawnSwarmResponse)
async def spawn_swarm(
    spawn_swarm_request: SpawnSwarmRequest,
    user_id: str = Depends(validate_token),
):
    try:
        swarm_id = spawn_swarm_request.swarm_id
        goal = spawn_swarm_request.goal

        if not swarm_id:
            raise HTTPException(status_code=400, detail="Swarm ID is required")
        if not goal:
            raise HTTPException(status_code=400, detail="Swarm goal is required")

        user_swarm = UserSwarm.get(swarm_id)
        user_swarm.update_on_spawn(goal)

        asyncio.create_task(_spawn_swarm(swarm_id, goal))

        return {"swarm": user_swarm.model_dump()}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
