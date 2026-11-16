from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_current_active_user, require_role
from app.modules.pedidos.models import EstadoPedido
from app.modules.pedidos.schemas import CambioEstado, PedidoCreate, PedidoRead, PedidosPaginados, ResumenPedidos
from app.modules.pedidos.service import PedidoAjeno, PedidoNoEncontrado, PedidoService, ProductoNoDisponible, ProductoNoEncontrado, ProductoRepetido, StockInsuficiente, TransicionInvalida
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])
service = PedidoService()

@router.get("/resumen", response_model=ResumenPedidos)
def resumen(admin: Usuario = Depends(require_role("admin"))) -> ResumenPedidos:
    return service.resumen()

@router.get("", response_model=PedidosPaginados)
def listar_pedidos(skip: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), estado: EstadoPedido | None = None, usuario: Usuario = Depends(get_current_active_user)) -> PedidosPaginados:
    return service.listar(skip, limit, estado, usuario)

@router.post("", response_model=PedidoRead, status_code=201)
def crear_pedido(data: PedidoCreate, usuario: Usuario = Depends(get_current_active_user)) -> PedidoRead:
    try:
        return service.crear(data, usuario)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (StockInsuficiente, ProductoNoDisponible, ProductoRepetido) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@router.get("/{pedido_id}", response_model=PedidoRead)
def obtener_pedido(pedido_id: int, usuario: Usuario = Depends(get_current_active_user)) -> PedidoRead:
    try:
        return service.obtener(pedido_id, usuario)
    except PedidoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PedidoAjeno as error:
        raise HTTPException(status_code=403, detail=str(error)) from error

@router.patch("/{pedido_id}/estado", response_model=PedidoRead)
def cambiar_estado(pedido_id: int, cambio: CambioEstado, admin: Usuario = Depends(require_role("admin"))) -> PedidoRead:
    try:
        return service.cambiar_estado(pedido_id, cambio)
    except PedidoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except TransicionInvalida as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@router.patch("/{pedido_id}/cancelar", response_model=PedidoRead)
def cancelar_pedido(pedido_id: int, usuario: Usuario = Depends(get_current_active_user)) -> PedidoRead:
    try:
        return service.cancelar_propio(pedido_id, usuario)
    except PedidoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PedidoAjeno as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except TransicionInvalida as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
