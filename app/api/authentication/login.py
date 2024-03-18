from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.utils.security import check_password, create_token
from app.models import User, UserProfile


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: User
    token: str


router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    username = login_request.username
    password = login_request.password

    user_profile = UserProfile.get(username)
    if not user_profile or not check_password(user_profile.password, password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = user_profile.user_id
    token = create_token(user_id)

    return {"user": User.get(user_id), "token": token}
