"""Request/response models for the onboarding assistant API."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(6, ge=1, le=12)


class Citation(BaseModel):
    doc: str
    owner: Optional[str] = None
    last_updated: Optional[date] = None
    snippet: str


class ConflictFlag(BaseModel):
    topic: str
    resolution: str
    losing_sources: list[str] = Field(default_factory=list)


class AskResponse(BaseModel):
    answer: str
    confidence: str
    citations: list[Citation] = Field(default_factory=list)
    conflicts: list[ConflictFlag] = Field(default_factory=list)
    latency_ms: int = 0