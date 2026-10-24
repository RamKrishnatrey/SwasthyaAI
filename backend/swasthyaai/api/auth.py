from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.swasthyaai.models.auth import LoginRequest, RegisterRequest, Session, User
from backend.swasthyaai.services.auth import (
    authenticate,
    create_user,
    get_current_user,
    revoke_token,
)

router = APIRouter(prefix="/auth")
_BEARER = HTTPBearer(auto_error=False)


@router.post("/register", response_model=User, status_code=201)
def register(request: RegisterRequest) -> User:
    try:
        return create_user(request.email, request.password, request.role)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/login", response_model=Session)
def login(request: LoginRequest) -> Session:
    session = authenticate(request.email, request.password)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return session


@router.get("/me", response_model=User)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/logout", status_code=204)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
    _user: User = Depends(get_current_user),
) -> Response:
    revoke_token(credentials.credentials)
    return Response(status_code=204)
