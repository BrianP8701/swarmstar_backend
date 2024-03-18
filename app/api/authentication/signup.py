from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.security import create_token
from app.models import User, UserProfile


class SignupRequest(BaseModel):
    username: str
    password: str


class SignupResponse(BaseModel):
    user: User
    token: str


router = APIRouter()


@router.put("/auth/signup", response_model=SignupResponse)
async def signup(signup_data: SignupRequest):
    username = signup_data.username
    password = signup_data.password

    try:
        UserProfile.get(username)
        raise HTTPException(status_code=401, detail="Username already exists")
    except ValueError:
        pass
    
    user_profile = UserProfile.create_new_user_profile(username, password)
    user = User.create_new_user(user_profile)
    token = create_token(user.id)

    return {"user": user, "token": token}
