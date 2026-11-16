from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.pedidos.models import EstadoPedido, FormaPago

class ItemPedidoCreate(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1)

class PedidoCreate(BaseModel):
    items: list[ItemPedidoCreate] = Field(min_length=1)
    forma_pago: FormaPago
    direccion_entrega: str = Field(min_length=5, max_length=200)
    notas: str | None = Field(default=None, max_length=500)

class DetallePedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: int
    nombre_producto: str
    precio_unitario: float
    subtotal: float

class PedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    estado: EstadoPedido
    forma_pago: FormaPago
    direccion_entrega: str
    notas: str | None
    total: float
    created_at: datetime
    updated_at: datetime
    items: list[DetallePedidoRead]

class PedidosPaginados(BaseModel):
    total: int
    items: list[PedidoRead]

class CambioEstado(BaseModel):
    estado: EstadoPedido

class ResumenPedidos(BaseModel):
    pendientes: int
    en_preparacion: int
    entregados: int
    cancelados: int
    pedidos_hoy: int
    ingresos_entregados: float
