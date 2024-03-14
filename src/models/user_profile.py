from pydantic import BaseModel

from src.database import MongoDBWrapper
from src.utils.security import generate_uuid, hash_password

db = MongoDBWrapper()

class UserProfile(BaseModel):
    id: str  # username
    password: str
    user_id: str

    @classmethod
    def get_user_profile(cls, username: str) -> 'UserProfile':
        return cls(**db.get("user_profiles", username))

    @classmethod
    def create_new_user_profile(cls, username: str, password: str) -> 'UserProfile':
        user_id = generate_uuid()
        hashed_password = hash_password(password)
        user_profile = cls(id=username, password=hashed_password, user_id=user_id)
        
        db.insert("user_profiles", username, user_profile.model_dump(exclude={'id'}))
        return user_profile

    @staticmethod
    def delete_user_profile( username: str) -> None:
        db.delete("user_profiles", username)
