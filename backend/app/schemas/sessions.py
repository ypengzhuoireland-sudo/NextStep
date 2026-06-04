from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str


class LoginResponse(BaseModel):
    student_id: str
    username: str
    name: str
    role: str
    access_token: str
    refresh_token: str
    token: str
    token_type: str
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token: str
    token_type: str
    expires_in: int


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class UserProfile(BaseModel):
    student_id: str
    username: str
    name: str
    role: str


class LogoutResponse(BaseModel):
    message: str


class DeleteAccountResponse(BaseModel):
    message: str
