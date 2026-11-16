from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.deps import require_role
from app.modules.categorias.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.modules.categorias.service import CategoriaNoEncontrada, CategoriaService, NombreDuplicado
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/categorias", tags=["Categorías"])
service = CategoriaService()

@router.get("", response_model=list[CategoriaRead])
def listar_categorias() -> list[CategoriaRead]:
    return service.listar()

@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(categoria_id: int) -> CategoriaRead:
    try:
        return service.obtener(categoria_id)
    except CategoriaNoEncontrada as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.post("", response_model=CategoriaRead, status_code=201)
def crear_categoria(data: CategoriaCreate, admin: Usuario = Depends(require_role("admin"))) -> CategoriaRead:
    try:
        return service.crear(data)
    except NombreDuplicado as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(categoria_id: int, data: CategoriaUpdate, admin: Usuario = Depends(require_role("admin"))) -> CategoriaRead:
    try:
        return service.actualizar(categoria_id, data)
    except CategoriaNoEncontrada as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except NombreDuplicado as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(categoria_id: int, admin: Usuario = Depends(require_role("admin"))) -> Response:
    try:
        service.eliminar(categoria_id)
        return Response(status_code=204)
    except CategoriaNoEncontrada as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
