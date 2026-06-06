from app.schemas.dashboard import Exercise


# Choose the exercise marked as recommended from the database-backed exercise list.
def choose_recommended_exercise(exercises: list[Exercise]) -> Exercise:
    return next((exercise for exercise in exercises if exercise.status == "recommended"), exercises[0])
