from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.security import validate_token
from app.models import UserSwarm, User

router = APIRouter()


class CreateSwarmRequest(BaseModel):
    swarm_name: str


class CreateSwarmResponse(BaseModel):
    swarm: UserSwarm
    user: User


@router.post("/swarm/create_swarm", response_model=CreateSwarmResponse)
async def create_swarm(
    create_swarm_request: CreateSwarmRequest, user_id: str = Depends(validate_token)
):
    try:
        new_swarm_name = create_swarm_request.swarm_name
        user = User.get_user(user_id)

        if not new_swarm_name:
            raise HTTPException(status_code=400, detail="Swarm name is required")
        if new_swarm_name in user.swarm_ids.values():
            raise HTTPException(status_code=400, detail="Swarm name already exists")

        user_swarm = UserSwarm.create_empty_user_swarm(user_id, new_swarm_name)
        user.add_swarm(user_swarm.id, new_swarm_name)
        user.set_current_swarm(user_swarm.id)
        
        return {"swarm": user_swarm, "user": User.get_user(user_id)}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
