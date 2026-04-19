import os
from pathlib import Path

from app.core.models import PipelineReport, QuarterSummary
from app.services.ingester import load_all_sessions
from app.services.validator import validate


class PipelineState:
    """In-memory state manager for the full pipeline report."""

    def __init__(self, sessions_dir: str | Path | None = None):
        configured_dir = sessions_dir or os.getenv("SESSIONS_DIR", "data")
        self.sessions_dir = Path(configured_dir)
        self._report: PipelineReport | None = None

    def initialize(self) -> None:
        """Load all sessions and cache a full report for request-time access."""
        if not self.sessions_dir.exists():
            raise RuntimeError(f"Sessions directory not found: {self.sessions_dir.resolve()}")

        raw_sessions = load_all_sessions(self.sessions_dir)
        results = validate(raw_sessions)

        summary = QuarterSummary(
            total_sessions_loaded=len(raw_sessions),
            total_sessions_valid=sum(1 for result in results if result.valid_entries > 0),
            total_entries_loaded=sum(result.total_entries for result in results),
            total_entries_valid=sum(result.valid_entries for result in results),
            final_sum=round(sum(result.valid_sum for result in results), 2),
        )
        self._report = PipelineReport(summary=summary, sessions=results)

    def get_report(self) -> PipelineReport:
        if self._report is None:
            raise RuntimeError("Pipeline not yet initialised.")
        return self._report


pipeline_state = PipelineState()
