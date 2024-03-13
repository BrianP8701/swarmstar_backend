from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from src.utils.database import get_user, get_user_profile
from src.utils.security import check_password, create_token
from src.types import User


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

    user_profile = get_user_profile(username)
    if not user_profile or not check_password(user_profile.password, password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = user_profile.user_id
    token = create_token(user_id)

    return {"user": get_user(user_id), "token": token}
