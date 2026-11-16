from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.core.deps import require_role
from app.modules.productos.schemas import ProductoCreate, ProductoRead, ProductoStockUpdate, ProductoUpdate, ProductosPaginados
from app.modules.productos.service import CategoriaProductoNoEncontrada, ProductoNoEncontrado, ProductoService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/productos", tags=["Productos"])
service = ProductoService()

@router.get("", response_model=ProductosPaginados)
def listar_productos(skip: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), search: str | None = None, categoria_id: int | None = Query(default=None, ge=1), disponible: bool | None = None) -> ProductosPaginados:
    return service.listar(skip, limit, search, categoria_id, disponible)

@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: int) -> ProductoRead:
    try:
        return service.obtener(producto_id)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.post("", response_model=ProductoRead, status_code=201)
def crear_producto(data: ProductoCreate, admin: Usuario = Depends(require_role("admin"))) -> ProductoRead:
    try:
        return service.crear(data)
    except CategoriaProductoNoEncontrada as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto(producto_id: int, data: ProductoUpdate, admin: Usuario = Depends(require_role("admin"))) -> ProductoRead:
    try:
        return service.actualizar(producto_id, data)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except CategoriaProductoNoEncontrada as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.patch("/{producto_id}/stock", response_model=ProductoRead)
def actualizar_stock(producto_id: int, data: ProductoStockUpdate, admin: Usuario = Depends(require_role("admin"))) -> ProductoRead:
    try:
        return service.actualizar_stock(producto_id, data)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, admin: Usuario = Depends(require_role("admin"))) -> Response:
    try:
        service.eliminar(producto_id)
        return Response(status_code=204)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
