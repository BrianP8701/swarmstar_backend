from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.security import validate_token
from app.models import UserSwarm, User, BackendChat, SwarmstarWrapper
from app.database import MongoDBWrapper

db = MongoDBWrapper()
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
        delete_user_swarm(swarm_id)

        return {"user": User.get_user(user_id), "swarm": None}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def delete_user_swarm(swarm_id: str):
    user_swarm = UserSwarm.get_user_swarm(swarm_id)
    
    for node_id in user_swarm.nodes_with_active_chat:
        BackendChat.delete_chat(node_id)
    for node_id in user_swarm.nodes_with_terminated_chat:
        BackendChat.delete_chat(node_id)
    db.delete("swarms", swarm_id)
    user = User.get_user(user_swarm.owner)
    del user.swarm_ids[swarm_id]
    if user.current_swarm_id == swarm_id:
        user.current_swarm_id = None
    user.update({"swarm_ids": user.swarm_ids, "current_swarm_id": user.current_swarm_id})

    if user_swarm.spawned:
        SwarmstarWrapper.delete_swarmstar_space(swarm_id)
