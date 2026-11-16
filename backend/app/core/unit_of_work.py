from sqlmodel import Session

from app.core.base_repository import BaseRepository
from app.core.database import engine
from app.modules.categorias.models import Categoria
from app.modules.categorias.repository import CategoriaRepository
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.repository import PedidoRepository
from app.modules.productos.models import Producto
from app.modules.productos.repository import ProductoRepository
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.repository import UsuarioRepository

class UnitOfWork:
    def __init__(self) -> None:
        self.session: Session | None = None

    def __enter__(self) -> "UnitOfWork":
        self.session = Session(engine)
        self.categorias = CategoriaRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.usuarios = UsuarioRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        self.detalles_pedido = BaseRepository(self.session, DetallePedido)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self.session is None:
            return False
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()
            self.session = None
        return False
