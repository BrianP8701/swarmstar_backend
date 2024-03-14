from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from src.utils.security import validate_token
from src.server.spawn_swarm import resume_swarm as _resume_swarm
from src.models import UserSwarm

router = APIRouter()


class ResumeSwarmRequest(BaseModel):
    swarm_id: str


class ResumeSwarmResponse(BaseModel):
    swarm: UserSwarm


@router.put("/swarm/resume_swarm", response_model=ResumeSwarmResponse)
async def resume_swarm(
    resume_swarm_request: ResumeSwarmRequest,
    user_id: str = Depends(validate_token),
):
    try:
        swarm_id = resume_swarm_request.swarm_id
        _resume_swarm(swarm_id)
        return {"swarm": UserSwarm.get_user_swarm(swarm_id)}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
