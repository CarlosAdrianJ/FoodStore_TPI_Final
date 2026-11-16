from datetime import datetime, timezone

from app.core.unit_of_work import UnitOfWork
from app.modules.pedidos.models import DetallePedido, EstadoPedido, Pedido
from app.modules.pedidos.schemas import CambioEstado, PedidoCreate, PedidoRead, PedidosPaginados, ResumenPedidos
from app.modules.usuarios.models import Usuario

class PedidoNoEncontrado(Exception):
    pass

class PedidoAjeno(Exception):
    pass

class ProductoNoEncontrado(Exception):
    pass

class StockInsuficiente(Exception):
    pass

class ProductoNoDisponible(Exception):
    pass

class ProductoRepetido(Exception):
    pass

class TransicionInvalida(Exception):
    pass

class PedidoService:
    def crear(self, data: PedidoCreate, usuario: Usuario) -> PedidoRead:
        ids = [item.producto_id for item in data.items]
        if len(ids) != len(set(ids)):
            raise ProductoRepetido("No se puede repetir un producto en el pedido")
        with UnitOfWork() as uow:
            lineas = []
            total = 0.0
            for item in data.items:
                producto = uow.productos.get_by_id(item.producto_id)
                if producto is None or not producto.activo:
                    raise ProductoNoEncontrado("Producto inexistente o inactivo")
                if not producto.disponible:
                    raise ProductoNoDisponible("Producto no disponible")
                if producto.stock < item.cantidad:
                    raise StockInsuficiente("Stock insuficiente")
                precio = float(producto.precio_base)
                subtotal = round(precio * item.cantidad, 2)
                total += subtotal
                producto.stock -= item.cantidad
                uow.productos.update(producto)
                lineas.append({"producto_id": producto.id, "cantidad": item.cantidad, "nombre_producto": producto.nombre, "precio_unitario": precio, "subtotal": subtotal})
            pedido = Pedido(usuario_id=usuario.id, forma_pago=data.forma_pago, direccion_entrega=data.direccion_entrega, notas=data.notas, total=round(total, 2))
            uow.pedidos.add(pedido)
            for linea in lineas:
                uow.detalles_pedido.add(DetallePedido(pedido_id=pedido.id, **linea))
            creado = uow.pedidos.get_con_items(pedido.id)
            return PedidoRead.model_validate(creado)

    def listar(self, skip: int, limit: int, estado: EstadoPedido | None, usuario: Usuario) -> PedidosPaginados:
        usuario_id = None if usuario.role == "admin" else usuario.id
        with UnitOfWork() as uow:
            total, pedidos = uow.pedidos.listar(skip, limit, usuario_id, estado)
            return PedidosPaginados(total=total, items=[PedidoRead.model_validate(item) for item in pedidos])

    def obtener(self, pedido_id: int, usuario: Usuario) -> PedidoRead:
        with UnitOfWork() as uow:
            pedido = uow.pedidos.get_con_items(pedido_id)
            if pedido is None:
                raise PedidoNoEncontrado("Pedido no encontrado")
            if usuario.role != "admin" and pedido.usuario_id != usuario.id:
                raise PedidoAjeno("El pedido pertenece a otro usuario")
            return PedidoRead.model_validate(pedido)

    def _reponer_stock(self, uow: UnitOfWork, pedido: Pedido) -> None:
        for linea in pedido.items:
            producto = uow.productos.get_by_id(linea.producto_id)
            if producto is not None:
                producto.stock += linea.cantidad
                uow.productos.update(producto)

    def cambiar_estado(self, pedido_id: int, cambio: CambioEstado) -> PedidoRead:
        transiciones = {EstadoPedido.PENDIENTE: {EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO}, EstadoPedido.EN_PREPARACION: {EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO}, EstadoPedido.ENTREGADO: set(), EstadoPedido.CANCELADO: set()}
        with UnitOfWork() as uow:
            pedido = uow.pedidos.get_con_items(pedido_id)
            if pedido is None:
                raise PedidoNoEncontrado("Pedido no encontrado")
            if cambio.estado not in transiciones[pedido.estado]:
                raise TransicionInvalida("Transición de estado inválida")
            if cambio.estado == EstadoPedido.CANCELADO:
                self._reponer_stock(uow, pedido)
            pedido.estado = cambio.estado
            pedido.updated_at = datetime.now(timezone.utc)
            uow.pedidos.update(pedido)
            actualizado = uow.pedidos.get_con_items(pedido_id)
            return PedidoRead.model_validate(actualizado)

    def cancelar_propio(self, pedido_id: int, usuario: Usuario) -> PedidoRead:
        with UnitOfWork() as uow:
            pedido = uow.pedidos.get_con_items(pedido_id)
            if pedido is None:
                raise PedidoNoEncontrado("Pedido no encontrado")
            if pedido.usuario_id != usuario.id:
                raise PedidoAjeno("El pedido pertenece a otro usuario")
            if pedido.estado != EstadoPedido.PENDIENTE:
                raise TransicionInvalida("Solo se cancela un pedido PENDIENTE")
            self._reponer_stock(uow, pedido)
            pedido.estado = EstadoPedido.CANCELADO
            pedido.updated_at = datetime.now(timezone.utc)
            uow.pedidos.update(pedido)
            actualizado = uow.pedidos.get_con_items(pedido_id)
            return PedidoRead.model_validate(actualizado)

    def resumen(self) -> ResumenPedidos:
        hoy = datetime.now(timezone.utc).date()
        with UnitOfWork() as uow:
            pedidos = uow.pedidos.get_all(limit=100000)
            entregados = [pedido for pedido in pedidos if pedido.estado == EstadoPedido.ENTREGADO]
            return ResumenPedidos(pendientes=uow.pedidos.count_by_estado(EstadoPedido.PENDIENTE), en_preparacion=uow.pedidos.count_by_estado(EstadoPedido.EN_PREPARACION), entregados=len(entregados), cancelados=uow.pedidos.count_by_estado(EstadoPedido.CANCELADO), pedidos_hoy=sum(1 for pedido in pedidos if pedido.created_at.date() == hoy), ingresos_entregados=round(sum(float(pedido.total) for pedido in entregados), 2))
