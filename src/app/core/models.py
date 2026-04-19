from datetime import datetime

from pydantic import BaseModel


class Entry(BaseModel):
    ref: str
    bin: str
    value: float
    category: str


class Session(BaseModel):
    session_id: str
    processor: str
    department: str
    timestamp: datetime
    entries: list[Entry]


class RejectedEntry(BaseModel):
    ref: str
    reasons: list[str]


class SessionResult(BaseModel):
    session_id: str
    processor: str
    department: str
    timestamp: datetime
    total_entries: int
    valid_entries: int
    valid_sum: float
    rejected: list[RejectedEntry]


class QuarterSummary(BaseModel):
    """Aggregate metrics for the full quarterly report."""

    total_sessions_loaded: int
    total_sessions_valid: int
    total_entries_loaded: int
    total_entries_valid: int
    final_sum: float


class PipelineReport(BaseModel):
    summary: QuarterSummary
    sessions: list[SessionResult]
