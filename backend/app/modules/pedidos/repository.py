from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.pedidos.models import EstadoPedido, Pedido

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_con_items(self, pedido_id: int) -> Pedido | None:
        statement = select(Pedido).options(selectinload(Pedido.items)).where(Pedido.id == pedido_id)
        return self.session.exec(statement).first()

    def listar(self, skip: int = 0, limit: int = 20, usuario_id: int | None = None, estado: EstadoPedido | None = None) -> tuple[int, list[Pedido]]:
        statement = select(Pedido)
        if usuario_id is not None:
            statement = statement.where(Pedido.usuario_id == usuario_id)
        if estado is not None:
            statement = statement.where(Pedido.estado == estado)
        total_statement = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(total_statement).one()
        items_statement = statement.options(selectinload(Pedido.items)).order_by(Pedido.created_at.desc()).offset(skip).limit(limit)
        items = list(self.session.exec(items_statement).all())
        return total, items

    def count_by_estado(self, estado: EstadoPedido) -> int:
        statement = select(func.count()).select_from(Pedido).where(Pedido.estado == estado)
        return self.session.exec(statement).one()
