from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "exercises.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    exercises = json.load(f)

exercise_by_id = {exercise["id"]: exercise for exercise in exercises}

core_kcs = sorted({
    kc
    for exercise in exercises
    for kc in exercise["kc_tags"]
})

students = {}


class Submission(BaseModel):
    student_id: str
    exercise_id: str
    correct: bool


def get_student(student_id: str):
    if student_id not in students:
        students[student_id] = {
            "mastery": {kc: 0.3 for kc in core_kcs},
            "completed": []
        }

    return students[student_id]


def update_mastery(old_mastery: float, correct: bool) -> float:
    if correct:
        return min(0.95, old_mastery + 0.15)
    return max(0.05, old_mastery - 0.10)


def recommend_next_exercise(student_id: str):
    student = get_student(student_id)
    mastery = student["mastery"]
    completed = set(student["completed"])

    weakest_kc = min(mastery, key=mastery.get)

    for exercise in exercises:
        if exercise["id"] not in completed and weakest_kc in exercise["kc_tags"]:
            return exercise

    for exercise in exercises:
        if exercise["id"] not in completed:
            return exercise

    return None


@app.get("/exercises")
def list_exercises():
    return exercises


@app.get("/exercises/next")
def get_next_exercise(student_id: str):
    exercise = recommend_next_exercise(student_id)

    if exercise is None:
        return {"message": "No exercises remaining"}

    return exercise


@app.get("/students/{student_id}/mastery")
def get_mastery(student_id: str):
    student = get_student(student_id)

    return {
        "student_id": student_id,
        "mastery": student["mastery"],
        "completed": student["completed"]
    }


@app.post("/submissions")
def submit_answer(submission: Submission):
    if submission.exercise_id not in exercise_by_id:
        raise HTTPException(status_code=404, detail="Exercise not found")

    student = get_student(submission.student_id)
    exercise = exercise_by_id[submission.exercise_id]

    for kc in exercise["kc_tags"]:
        old_value = student["mastery"].get(kc, 0.3)
        student["mastery"][kc] = update_mastery(old_value, submission.correct)

    if submission.exercise_id not in student["completed"]:
        student["completed"].append(submission.exercise_id)

    next_exercise = recommend_next_exercise(submission.student_id)
    next_exercise_id = None

    if next_exercise is not None:
        next_exercise_id = next_exercise["id"]

    return {
        "student_id": submission.student_id,
        "exercise_id": submission.exercise_id,
        "correct": submission.correct,
        "updated_mastery": student["mastery"],
        "next_recommended_exercise_id": next_exercise_id
    }

@app.get("/")
def root():
    return {
        "message": "Adaptive AI Tutor API is running",
        "docs": "/docs"
    }