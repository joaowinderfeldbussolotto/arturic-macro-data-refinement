import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.pipeline import pipeline_state

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and validate all sessions once when the server starts."""
    pipeline_state.initialize()
    report = pipeline_state.get_report()
    logger.info(
        "Pipeline ready — %d valid entries, final sum: %.2f",
        report.summary.total_entries_valid,
        report.summary.final_sum,
    )
    yield


app = FastAPI(
    title="Macro Data Refinement API",
    description=(
        "Processes quarterly session output files against the Arturic Industries "
        "compliance ruleset and exposes the validated results."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(v1_router, prefix="/api/v1")
