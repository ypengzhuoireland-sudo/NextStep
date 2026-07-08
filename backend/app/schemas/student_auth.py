from pydantic import BaseModel, Field


class StudentUser(BaseModel):
    id: str
    name: str
    email: str
    avatarInitials: str
    needsDiagnostic: bool


class StudentLoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class StudentRegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class StudentAuthResponse(BaseModel):
    token: str
    user: StudentUser


class StudentMeResponse(BaseModel):
    user: StudentUser


class StudentMessageResponse(BaseModel):
    message: str
