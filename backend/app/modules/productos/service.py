from app.core.unit_of_work import UnitOfWork
from app.modules.productos.models import Producto
from app.modules.productos.schemas import ProductoCreate, ProductoRead, ProductoStockUpdate, ProductoUpdate, ProductosPaginados

class ProductoNoEncontrado(Exception):
    pass

class CategoriaProductoNoEncontrada(Exception):
    pass

class ProductoService:
    def listar(self, skip: int = 0, limit: int = 20, search: str | None = None, categoria_id: int | None = None, disponible: bool | None = None) -> ProductosPaginados:
        with UnitOfWork() as uow:
            total, items = uow.productos.buscar_catalogo(skip, limit, search, categoria_id, disponible)
            return ProductosPaginados(total=total, items=[ProductoRead.model_validate(item) for item in items])

    def obtener(self, producto_id: int) -> ProductoRead:
        with UnitOfWork() as uow:
            producto = uow.productos.get_by_id(producto_id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado("Producto no encontrado")
            return ProductoRead.model_validate(producto)

    def crear(self, data: ProductoCreate) -> ProductoRead:
        with UnitOfWork() as uow:
            categoria = uow.categorias.get_by_id(data.categoria_id)
            if categoria is None or not categoria.activo:
                raise CategoriaProductoNoEncontrada("Categoría inexistente o inactiva")
            producto = Producto(**data.model_dump())
            uow.productos.add(producto)
            return ProductoRead.model_validate(producto)

    def actualizar(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
        cambios = data.model_dump(exclude_unset=True, exclude_none=True)
        with UnitOfWork() as uow:
            producto = uow.productos.get_by_id(producto_id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado("Producto no encontrado")
            if "categoria_id" in cambios:
                categoria = uow.categorias.get_by_id(cambios["categoria_id"])
                if categoria is None or not categoria.activo:
                    raise CategoriaProductoNoEncontrada("Categoría inexistente o inactiva")
            for campo, valor in cambios.items():
                setattr(producto, campo, valor)
            uow.productos.update(producto)
            return ProductoRead.model_validate(producto)

    def actualizar_stock(self, producto_id: int, data: ProductoStockUpdate) -> ProductoRead:
        with UnitOfWork() as uow:
            producto = uow.productos.get_by_id(producto_id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado("Producto no encontrado")
            producto.stock = data.stock
            producto.disponible = data.disponible
            uow.productos.update(producto)
            return ProductoRead.model_validate(producto)

    def eliminar(self, producto_id: int) -> None:
        with UnitOfWork() as uow:
            producto = uow.productos.get_by_id(producto_id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado("Producto no encontrado")
            producto.activo = False
            uow.productos.update(producto)
