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
    def get(cls, message_id: str):
        return cls(**db.get("messages", message_id))

    def save(self):
        db.insert("messages", self.id, self.model_dump(exclude={'id'}))

    @staticmethod
    def delete(message_id: str):
        db.delete("messages", message_id)
        

class BackendChat(BaseModel):
    """
    This is the chat object thats actually stored in the database.
    """
    id: str  # node_id
    message_ids: List[str]  # List of message ids
    alive: bool
    user_communication_operation: Optional[UserCommunicationOperation] = None

    @classmethod
    def get(cls, node_id: str):
        return cls(**db.get("chats", node_id))

    @classmethod
    def create_empty_chat(cls, node_id: str) -> 'BackendChat':
        chat = cls(id=node_id, message_ids=[], alive=True)
        db.insert("chats", chat.id, chat.model_dump(exclude={'id'}))
        return chat

    def append_message(self, message_id: str):
        db.append_to_list("chats", self.id, "message_ids", message_id)

    def update(self, updated_values: dict):
        db.update("chats", self.id, updated_values)

    def replace(self):
        db.replace("chats", self.id, self.model_dump(exclude={'id'}))

    @staticmethod
    def delete(node_id: str):
        chat = BackendChat.get(node_id)
        for message_id in chat.message_ids:
            SwarmMessage.delete(message_id)
        db.delete("chats", node_id)
            

class Chat(BaseModel):
    """ This is the chat object that is returned to the frontend. """
    id: str  # node_id
    messages: List[SwarmMessage]  # List of messages
    alive: bool

    @staticmethod
    def get(node_id: str) -> 'Chat':
        chat = BackendChat.get(node_id)
        messages = [SwarmMessage.get(message_id) for message_id in chat.message_ids]
        return Chat(id=chat.id, messages=messages, alive=chat.alive)
