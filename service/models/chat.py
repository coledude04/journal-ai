from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class CreateChatRequest(BaseModel):
    chatName: str
    feedbackId: str | None = None


class SendMessageRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    messageId: str
    sender: Literal["user", "assistant"]
    message: str
    createdAt: datetime


class Chat(BaseModel):
    chatId: str
    userId: str
    feedbackId: str | None = None
    chatName: str
    createdAt: datetime
    updatedAt: datetime
    messages: list[ChatMessage] = []


class ChatSummary(BaseModel):
    chatId: str
    chatName: str
    feedbackId: str | None = None
    createdAt: datetime
    updatedAt: datetime


class ChatPage(BaseModel):
    items: list[ChatSummary]
    nextPageToken: str | None = None
