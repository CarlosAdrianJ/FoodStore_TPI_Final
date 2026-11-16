from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.modules.usuarios.models import Usuario

def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
) -> Usuario:
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Sesión inválida o vencida', headers={'WWW-Authenticate': 'Bearer'})
    if not access_token:
        raise credentials_error
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get('sub')
        if not isinstance(username, str) or not username:
            raise credentials_error
    except JWTError as error:
        raise credentials_error from error
    user = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if user is None:
        raise credentials_error
    return user

def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Cuenta de usuario desactivada')
    return current_user

def require_role(role: str):
    def role_checker(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        if current_user.role != role:
            raise HTTPException(status_code=403, detail='Rol no permitido')
        return current_user
    return role_checker
