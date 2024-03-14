from fastapi import Depends, APIRouter, HTTPException

from src.utils.security import validate_token
from src.models import User

router = APIRouter()

@router.delete("/user/delete_user")
async def delete_user(user_id: str = Depends(validate_token)):
    try:
        User.delete_user(user_id)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
