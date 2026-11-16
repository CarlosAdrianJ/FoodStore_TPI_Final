from fastapi import HTTPException

from app.core.security import hash_password, verify_password
from app.core.unit_of_work import UnitOfWork
from app.modules.auth.schemas import UserCreate, UserPublic
from app.modules.usuarios.models import Usuario

class AuthService:
    def register(self, data: UserCreate) -> UserPublic:
        username = data.username.strip()
        email = str(data.email).lower()
        with UnitOfWork() as uow:
            if uow.usuarios.get_by_username(username) or uow.usuarios.get_by_email(email):
                raise HTTPException(status_code=409, detail="El username o email ya existe")
            user = Usuario(username=username, full_name=data.full_name.strip(), email=email, hashed_password=hash_password(data.password), role="user", disabled=False)
            uow.usuarios.add(user)
            return UserPublic.model_validate(user)

    def authenticate(self, username: str, password: str) -> str:
        with UnitOfWork() as uow:
            user = uow.usuarios.get_by_username(username)
            if user is None or not verify_password(password, user.hashed_password):
                raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            if user.disabled:
                raise HTTPException(status_code=400, detail="Cuenta de usuario desactivada")
            return user.username
