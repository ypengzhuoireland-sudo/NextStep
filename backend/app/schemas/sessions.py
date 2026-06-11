from pydantic import BaseModel


class UserProfile(BaseModel):
    student_id: str
    username: str
    name: str
    role: str
