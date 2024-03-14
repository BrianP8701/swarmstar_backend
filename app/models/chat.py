from pydantic import BaseModel, Field
from typing import Optional, List

from swarmstar.models import UserCommunicationOperation

from app.utils.security.generate_uuid import generate_uuid
from app.database import MongoDBWrapper

db = MongoDBWrapper()

class SwarmMessage(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid("message"))
    role: str
    content: str

    @classmethod
    def get_message(cls, message_id: str):
        return cls(**db.get("messages", message_id))

    def create(self):
        db.insert("messages", self.id, self.model_dump(exclude={'id'}))

    @staticmethod
    def delete(message_id: str):
        db.delete("messages", message_id)
        

class BackendChat(BaseModel):
    id: str  # node_id
    message_ids: List[str]  # List of message ids
    alive: bool
    user_communication_operation: Optional[UserCommunicationOperation] = None

    @classmethod
    def get_chat(cls, node_id: str):
        return cls(**db.get("chats", node_id))

    @classmethod
    def create_empty_chat(cls, node_id: str):
        chat = cls(id=node_id, message_ids=[], alive=True)
        db.insert("chats", chat.id, chat.model_dump(exclude={'id'}))
        return chat

    def append_message(self, message_id: str):
        db.append("chats", self.id, {"message_ids": message_id})
        self.message_ids.append(message_id)

    def update(self, updated_values: dict):
        db.update("chats", self.id, updated_values)
        for field, value in updated_values.items():
            setattr(self, field, value)

    @staticmethod
    def delete_chat(node_id: str):
        chat = BackendChat.get_chat(node_id)
        for message_id in chat.message_ids:
            SwarmMessage.delete(message_id)
        db.delete("chats", node_id)
            

class Chat(BaseModel):
    id: str  # node_id
    messages: List[SwarmMessage]  # List of messages
    alive: bool

    @classmethod
    def get_chat(cls, node_id: str):
        chat = BackendChat.get_chat(node_id)
        messages = [SwarmMessage.get_message(message_id) for message_id in chat.message_ids]
        return cls(id=chat.id, messages=messages, alive=chat.alive)
