from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from typing import Optional

from app.utils.security import validate_token
from app.models import UserSwarm, User

router = APIRouter()

class CopySwarmRequest(BaseModel):
    swarm_name: str
    old_swarm_id: str


class CopySwarmResponse(BaseModel):
    swarm: UserSwarm
    user: User
    swarm_tree: Optional[dict] = None


@router.post("/swarm/copy_swarm", response_model=CopySwarmResponse)
async def create_swarm(
    create_swarm_request: CopySwarmRequest, user_id: str = Depends(validate_token)
):
    try:
        new_swarm_name = create_swarm_request.swarm_name
        old_swarm_id = create_swarm_request.old_swarm_id
        user = User.get(user_id)

        if not new_swarm_name:
            raise HTTPException(status_code=400, detail="Swarm name is required")
        if new_swarm_name in user.swarm_ids.values():
            raise HTTPException(status_code=400, detail="Swarm name already exists")

        user_swarm = UserSwarm.duplicate(user_id, new_swarm_name, old_swarm_id)
        swarm_tree = UserSwarm.get_tree(user_swarm.id)
        
        return {"swarm": user_swarm, "user": User.get(user_id), "swarm_tree": swarm_tree}
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
