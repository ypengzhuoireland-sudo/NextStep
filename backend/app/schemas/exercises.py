from pydantic import BaseModel


# Represent one expected input/output pair for an exercise.
class TestCase(BaseModel):
    input: str
    expected_output: str


# Represent one exercise row in exercise lists and dashboard queues.
class ExerciseSummary(BaseModel):
    id: str
    title: str
    kc: str
    difficulty: str
    status: str


# Represent the full exercise payload needed by the practice page.
class ExerciseDetail(ExerciseSummary):
    description: str
    starter_code: str
    test_cases: list[TestCase]
