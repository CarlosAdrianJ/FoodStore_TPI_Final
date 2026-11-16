from fastapi import APIRouter, Depends

from app.core.deps import require_role
from app.modules.auth.schemas import UserPublic
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.service import UsuarioAdminService

router = APIRouter(prefix="/admin/usuarios", tags=["Usuarios"])
service = UsuarioAdminService()

@router.get("", response_model=list[UserPublic])
def listar_usuarios(admin: Usuario = Depends(require_role("admin"))) -> list[UserPublic]:
    return service.listar()

@router.post("/{user_id}/activar", response_model=UserPublic)
def activar_usuario(user_id: int, admin: Usuario = Depends(require_role("admin"))) -> UserPublic:
    return service.activar(user_id)

@router.post("/{user_id}/desactivar", response_model=UserPublic)
def desactivar_usuario(user_id: int, admin: Usuario = Depends(require_role("admin"))) -> UserPublic:
    return service.desactivar(user_id, admin.id)
