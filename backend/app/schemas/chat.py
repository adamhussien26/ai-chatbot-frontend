"""
schemas/chat.py — مخططات المحادثة
"""
from datetime import datetime

from pydantic import BaseModel, Field


class ChatQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class ChatAnswer(BaseModel):
    answer: str
    source: str                    # database / rag / llm
    source_ref: str | None = None
    intent: str | None = None


class ChatHistoryOut(BaseModel):
    id: int
    question: str
    answer: str
    source: str
    source_ref: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
