from pydantic import BaseModel, Field
from typing import Optional, List

from swarmstar.types import UserCommunicationOperation

from src.utils.security.generate_uuid import generate_uuid
from src.database import MongoDBWrapper

mdb = MongoDBWrapper()

class SwarmMessage(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid("message"))
    role: str
    content: str

    @classmethod
    def get_message(cls, message_id: str):
        return cls(**mdb.get("messages", message_id))

    def create(self):
        mdb.insert("messages", self.id, self.model_dump(exclude={'id'}))

class BackendChat(BaseModel):
    id: str  # node_id
    message_ids: List[str]  # List of message ids
    alive: bool
    user_communication_operation: Optional[UserCommunicationOperation] = None

    @classmethod
    def get_chat(cls, node_id: str):
        return cls(**mdb.get("chats", node_id))

    @classmethod
    def create_empty_chat(cls, node_id: str):
        chat = cls(id=node_id, message_ids=[], alive=True)
        mdb.insert("chats", chat.id, chat.model_dump(exclude={'id'}))
        return chat

    def append_message(self, message_id: str):
        mdb.append("chats", self.id, {"message_ids": message_id})
        self.message_ids.append(message_id)

    def update(self, updated_values: dict):
        mdb.update("chats", self.id, updated_values)
        for field, value in updated_values.items():
            setattr(self, field, value)

class Chat(BaseModel):
    id: str  # node_id
    messages: List[SwarmMessage]  # List of messages
    alive: bool

    @classmethod
    def get_node_chat(cls, node_id: str):
        chat = BackendChat.get_chat(node_id)
        messages = [SwarmMessage.get_message(message_id) for message_id in chat.message_ids]
        return cls(id=chat.id, messages=messages, alive=chat.alive)
