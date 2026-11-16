from fastapi import HTTPException

from app.core.unit_of_work import UnitOfWork
from app.modules.auth.schemas import UserPublic
from app.modules.usuarios.models import Usuario

class UsuarioAdminService:
    def listar(self) -> list[UserPublic]:
        with UnitOfWork() as uow:
            return [UserPublic.model_validate(user) for user in uow.usuarios.listar()]

    def activar(self, user_id: int) -> UserPublic:
        with UnitOfWork() as uow:
            user = uow.usuarios.get_by_id(user_id)
            if user is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            user.disabled = False
            uow.usuarios.update(user)
            return UserPublic.model_validate(user)

    def desactivar(self, user_id: int, admin_id: int) -> UserPublic:
        if user_id == admin_id:
            raise HTTPException(status_code=400, detail="El administrador no puede desactivarse a sí mismo")
        with UnitOfWork() as uow:
            user = uow.usuarios.get_by_id(user_id)
            if user is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            user.disabled = True
            uow.usuarios.update(user)
            return UserPublic.model_validate(user)
