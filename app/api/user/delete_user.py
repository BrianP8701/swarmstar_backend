from fastapi import Depends, APIRouter, HTTPException

from app.utils.security import validate_token
from app.models import User, UserSwarm
from app.database import MongoDBWrapper

db = MongoDBWrapper()

router = APIRouter()

@router.delete("/user/delete_user")
async def delete_user(user_id: str = Depends(validate_token)):
    try:
        User.delete(user_id)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def delete_user(cls, user_id: str):
    user = cls.get_user(user_id)
    username = user.username
    for swarm_id in user.swarm_ids:
        UserSwarm.delete_user_swarm(swarm_id)
    db.delete("users", user_id)
    db.delete("user_profiles", username)