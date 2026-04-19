from fastapi import APIRouter, Depends, HTTPException

from app.core.models import PipelineReport
from app.core.pipeline import pipeline_state

router = APIRouter()


def get_pipeline_report() -> PipelineReport:
    try:
        return pipeline_state.get_report()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/health", tags=["meta"], summary="Health check")
def health() -> dict[str, str]:
    """Returns 200 when the service is running and the pipeline is ready."""
    return {"status": "ok"}


@router.get(
    "/report",
    response_model=PipelineReport,
    tags=["pipeline"],
    summary="Full pipeline report",
)
def get_report(report: PipelineReport = Depends(get_pipeline_report)) -> PipelineReport:
    """Return the complete pipeline report with summary and all sessions."""
    return report


@router.get(
    "/result",
    tags=["pipeline"],
    summary="Final output metric",
)
def get_result(report: PipelineReport = Depends(get_pipeline_report)) -> dict[str, float | int]:
    """Return only the final metric and headline counts."""
    return {
        "final_sum": report.summary.final_sum,
        "valid_entries": report.summary.total_entries_valid,
        "total_entries": report.summary.total_entries_loaded,
    }
