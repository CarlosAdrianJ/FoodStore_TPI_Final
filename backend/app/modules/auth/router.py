from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.deps import get_current_active_user
from app.core.security import create_access_token
from app.modules.auth.schemas import UserCreate, UserPublic
from app.modules.auth.service import AuthService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])
service = AuthService()

@router.post("/register", response_model=UserPublic, status_code=201)
def register(data: UserCreate) -> UserPublic:
    return service.register(data)

@router.post("/token")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    username = service.authenticate(form_data.username, form_data.password)
    token = create_access_token(username)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=settings.access_token_expire_minutes * 60, path="/api/v1", samesite="lax", secure=settings.frontend_origin.startswith("https://"))
    return {"message": "Login exitoso"}

@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key="access_token", path="/api/v1")
    return {"message": "Logout exitoso"}

@router.get("/me", response_model=UserPublic)
def me(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    return current_user
