from pydantic import BaseModel, Field


# Define the request body accepted by POST /api/executions/run.
class ExecutionRunRequest(BaseModel):
    code: str = Field(min_length=1)
    language: str = "python"
    stdin: str = ""
    expected_output: str | None = None


# Define the normalized execution result returned to the frontend.
class ExecutionRunResponse(BaseModel):
    passed: bool
    stdout: str
    stderr: str
    compile_output: str
    message: str
    status_id: int | None
    status_description: str
    time: str | None
    memory: int | None
    token: str | None
