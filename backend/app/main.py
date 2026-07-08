from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

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
from app.api.submissions import router as submissions_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_auth_router, prefix="/api")
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


@app.get("/")
def root():
    return RedirectResponse(url="/docs")
