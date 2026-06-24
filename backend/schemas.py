"""Request/response models for the onboarding assistant API."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(8, ge=1, le=12)


class Citation(BaseModel):
    doc: str
    owner: Optional[str] = None
    # Kept as a tolerant string, not a `date`: the model legitimately emits
    # "unknown" for undated docs, and a strict date type turned that into a
    # validation error that silently collapsed the whole structured answer.
    last_updated: Optional[str] = None
    snippet: str = ""

    @field_validator("last_updated", "owner", mode="before")
    @classmethod
    def _blank_to_none(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        if s.lower() in ("", "unknown", "n/a", "none", "null"):
            return None
        return s


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