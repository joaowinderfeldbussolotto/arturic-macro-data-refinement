from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.endpoints.pipeline import get_pipeline_report
from app.core.models import PipelineReport, SessionResult

router = APIRouter()


@router.get(
    "/sessions",
    response_model=list[SessionResult],
    tags=["sessions"],
    summary="List session results",
)
def list_sessions(
    department: str | None = Query(None, description="Filter by department code (MDR, SA, WB)."),
    valid_only: bool = Query(False, description="When true, return only sessions with at least one valid entry."),
    report: PipelineReport = Depends(get_pipeline_report),
) -> list[SessionResult]:
    """Return validation results for all sessions, with optional filtering."""
    sessions = report.sessions

    if department:
        sessions = [session for session in sessions if session.department == department.upper()]
    if valid_only:
        sessions = [session for session in sessions if session.valid_entries > 0]

    return sessions


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResult,
    tags=["sessions"],
    summary="Single session result",
)
def get_session(session_id: str, report: PipelineReport = Depends(get_pipeline_report)) -> SessionResult:
    """Return the validation result for a specific session ID."""
    for session in report.sessions:
        if session.session_id == session_id:
            return session
    raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
