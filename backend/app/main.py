import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.assistant import router as assistant_router
from app.api.dashboard import router as dashboard_router
from app.api.diagnostic import router as diagnostic_router
from app.api.evaluation import router as evaluation_router
from app.api.executions import router as executions_router
from app.api.exercises import router as exercises_router
from app.api.kcs import router as kcs_router
from app.api.learning_advice import router as learning_advice_router
from app.api.mastery import router as mastery_router
from app.api.practice import router as practice_router
from app.api.recommendations import router as recommendations_router
from app.api.student_auth import router as student_auth_router
from app.api.student_auth import teacher_router
from app.api.submissions import router as submissions_router

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
FRONTEND_DIST = Path(__file__).resolve().parents[1] / "static"


def get_allowed_origins() -> list[str]:
    configured_origins = [
        origin.strip().rstrip("/")
        for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]
    return list(dict.fromkeys([*DEFAULT_ALLOWED_ORIGINS, *configured_origins]))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_auth_router, prefix="/api")
app.include_router(teacher_router, prefix="/api")
app.include_router(assistant_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(diagnostic_router, prefix="/api")
app.include_router(evaluation_router, prefix="/api", tags=["evaluation"])
app.include_router(executions_router, prefix="/api", tags=["executions"])
app.include_router(exercises_router, prefix="/api", tags=["exercises"])
app.include_router(kcs_router, prefix="/api", tags=["kcs"])
app.include_router(learning_advice_router, prefix="/api", tags=["learning-advice"])
app.include_router(mastery_router, prefix="/api", tags=["mastery"])
app.include_router(practice_router, prefix="/api", tags=["practice"])
app.include_router(recommendations_router, prefix="/api", tags=["recommendations"])
app.include_router(submissions_router, prefix="/api", tags=["submissions"])


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    def frontend_index():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_app(full_path: str):
        if full_path.startswith(("api/", "docs", "openapi.json", "redoc")):
            raise HTTPException(status_code=404)

        requested_path = FRONTEND_DIST / full_path
        if requested_path.is_file():
            return FileResponse(requested_path)

        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root():
        return RedirectResponse(url="/docs")
