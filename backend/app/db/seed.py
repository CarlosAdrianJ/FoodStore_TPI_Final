from sqlmodel import SQLModel

from app import models
from app.core.database import engine
from app.core.security import hash_password
from app.core.unit_of_work import UnitOfWork
from app.modules.categorias.models import Categoria
from app.modules.productos.models import Producto
from app.modules.usuarios.models import Usuario

CATEGORIAS = [("Hamburguesas", "Hamburguesas y sándwiches"), ("Pizzas", "Pizzas artesanales"), ("Guarniciones", "Acompañamientos"), ("Bebidas", "Bebidas frías")]

PRODUCTOS = [("Hamburguesa clásica", "Hamburguesa con queso", 4500.0, "Hamburguesas"), ("Hamburguesa completa", "Hamburguesa completa de la casa", 5200.0, "Hamburguesas"), ("Hamburguesa veggie", "Hamburguesa vegetariana", 4800.0, "Hamburguesas"), ("Pizza muzzarella", "Pizza clásica de muzzarella", 6000.0, "Pizzas"), ("Pizza napolitana", "Pizza con tomate y muzzarella", 7000.0, "Pizzas"), ("Papas fritas", "Porción de papas fritas", 2000.0, "Guarniciones"), ("Gaseosa cola", "Botella de gaseosa cola", 1500.0, "Bebidas"), ("Agua mineral", "Botella de agua mineral", 1200.0, "Bebidas")]

def seed() -> None:
    SQLModel.metadata.create_all(engine)
    with UnitOfWork() as uow:
        admin = uow.usuarios.get_by_username("admin")
        if admin is None:
            admin = Usuario(username="admin", full_name="Administrador", email="admin@foodstore.com", hashed_password=hash_password("Admin1234!"), role="admin", disabled=False)
            uow.usuarios.add(admin)
        else:
            admin.role = "admin"
            admin.disabled = False
            uow.usuarios.update(admin)

        categorias = {}
        for nombre, descripcion in CATEGORIAS:
            categoria = uow.categorias.get_by_nombre(nombre)
            if categoria is None:
                categoria = uow.categorias.add(Categoria(nombre=nombre, descripcion=descripcion, activo=True))
            elif not categoria.activo:
                categoria.activo = True
                uow.categorias.update(categoria)
            categorias[nombre] = categoria

        nombres_existentes = {producto.nombre for producto in uow.productos.get_all(limit=10000)}
        for nombre, descripcion, precio, categoria_nombre in PRODUCTOS:
            if nombre not in nombres_existentes:
                uow.productos.add(Producto(categoria_id=categorias[categoria_nombre].id, nombre=nombre, descripcion=descripcion, precio_base=precio, imagen_url=None, stock=30, disponible=True, activo=True))

    print("Seed listo: administrador, categorías y productos cargados.")

if __name__ == "__main__":
    seed()

