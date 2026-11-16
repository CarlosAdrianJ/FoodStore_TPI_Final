from sqlalchemy import func
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.productos.models import Producto

class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def buscar_catalogo(self, skip: int = 0, limit: int = 20, search: str | None = None, categoria_id: int | None = None, disponible: bool | None = None) -> tuple[int, list[Producto]]:
        statement = select(Producto).where(Producto.activo.is_(True))
        if search:
            statement = statement.where(Producto.nombre.ilike("%" + search + "%"))
        if categoria_id is not None:
            statement = statement.where(Producto.categoria_id == categoria_id)
        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)
        total_statement = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(total_statement).one()
        items_statement = statement.order_by(Producto.nombre).offset(skip).limit(limit)
        items = list(self.session.exec(items_statement).all())
        return total, items

    def get_activos_de_categoria(self, categoria_id: int) -> list[Producto]:
        statement = select(Producto).where(Producto.categoria_id == categoria_id, Producto.activo.is_(True))
        return list(self.session.exec(statement).all())
