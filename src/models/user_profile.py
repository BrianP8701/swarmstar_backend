from pydantic import BaseModel
from src.database import MongoDBWrapper

mdb = MongoDBWrapper()

class UserProfile(BaseModel):
    id: str  # username
    password: str
    user_id: str

    @classmethod
    def get_user_profile(cls, username: str):
        return cls(**mdb.get("user_profiles", username))

    @classmethod
    def create_new_user_profile(cls, username: str, password: str, user_id: str):
        user_profile = cls(id=username, password=password, user_id=user_id)
        mdb.insert("user_profiles", username, user_profile.model_dump(exclude={'id'}))
        return user_profile

    @classmethod
    def delete_user_profile(cls, username: str):
        mdb.delete("user_profiles", username)