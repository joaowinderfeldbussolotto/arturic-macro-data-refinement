from fastapi import APIRouter

from app.api.v1.endpoints import pipeline, sessions

router = APIRouter()
router.include_router(pipeline.router)
router.include_router(sessions.router)
