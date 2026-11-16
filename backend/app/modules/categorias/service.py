from app.core.unit_of_work import UnitOfWork
from app.modules.categorias.models import Categoria
from app.modules.categorias.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate

class CategoriaNoEncontrada(Exception):
    pass

class NombreDuplicado(Exception):
    pass

class CategoriaService:
    def listar(self) -> list[CategoriaRead]:
        with UnitOfWork() as uow:
            return [CategoriaRead.model_validate(item) for item in uow.categorias.get_activas()]

    def obtener(self, categoria_id: int) -> CategoriaRead:
        with UnitOfWork() as uow:
            categoria = uow.categorias.get_by_id(categoria_id)
            if categoria is None or not categoria.activo:
                raise CategoriaNoEncontrada("Categoría no encontrada")
            return CategoriaRead.model_validate(categoria)

    def crear(self, data: CategoriaCreate) -> CategoriaRead:
        with UnitOfWork() as uow:
            if uow.categorias.get_by_nombre(data.nombre):
                raise NombreDuplicado("El nombre de categoría ya existe")
            categoria = Categoria(**data.model_dump())
            uow.categorias.add(categoria)
            return CategoriaRead.model_validate(categoria)

    def actualizar(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaRead:
        cambios = data.model_dump(exclude_unset=True)
        with UnitOfWork() as uow:
            categoria = uow.categorias.get_by_id(categoria_id)
            if categoria is None or not categoria.activo:
                raise CategoriaNoEncontrada("Categoría no encontrada")
            if "nombre" in cambios and cambios["nombre"] != categoria.nombre and uow.categorias.get_by_nombre(cambios["nombre"]):
                raise NombreDuplicado("El nombre de categoría ya existe")
            for campo, valor in cambios.items():
                setattr(categoria, campo, valor)
            uow.categorias.update(categoria)
            return CategoriaRead.model_validate(categoria)

    def eliminar(self, categoria_id: int) -> None:
        with UnitOfWork() as uow:
            categoria = uow.categorias.get_by_id(categoria_id)
            if categoria is None or not categoria.activo:
                raise CategoriaNoEncontrada("Categoría no encontrada")
            categoria.activo = False
            for producto in uow.productos.get_activos_de_categoria(categoria_id):
                producto.activo = False
                uow.productos.update(producto)
            uow.categorias.update(categoria)
