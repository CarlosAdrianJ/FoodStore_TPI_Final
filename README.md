# Food Store — Sistema de pedidos

Trabajo Práctico Integrador de Programación IV. Aplicación web para consultar un catálogo, realizar pedidos y administrarlos.

## Tecnologías

- Backend: Python, FastAPI, SQLModel y PostgreSQL.
- Frontend: React, TypeScript, Vite y Tailwind CSS.
- Autenticación con JWT en cookie HttpOnly y autorización por roles.

## Requisitos

- Python 3.11 a 3.13.
- PostgreSQL 15 o superior.
- Node.js 20 o superior.
- pnpm 9 o superior.

## Repositorio y demostración

- Repositorio público: [FoodStore_TPI_Final](https://github.com/CarlosAdrianJ/FoodStore_TPI_Final)
- Video público de demostración: **PEGAR AQUÍ EL ENLACE DEL VIDEO**

## Configuración del backend

Iniciá PostgreSQL. Si la base `foodstore_tpi_final` todavía no existe, creala con:

```powershell
psql -U postgres -h localhost -p 5432 -d postgres -c "CREATE DATABASE foodstore_tpi_final;"
```

Desde PowerShell, en la carpeta raíz del proyecto:

```powershell
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Editá `backend/.env`. En `DATABASE_URL`, reemplazá `user` y `password` por las credenciales de PostgreSQL. Generá una clave secreta con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiá el resultado en `SECRET_KEY`. No publiques el archivo `.env` ni compartas su contenido.

Cargá el administrador, las categorías y los productos; luego iniciá el servidor:

```powershell
python -m app.db.seed
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000/api/v1`. La documentación interactiva está en `http://localhost:8000/docs`.

Credenciales de desarrollo del administrador: usuario `admin`, contraseña `Admin1234!`.

## Configuración del frontend

Abrí otra terminal de PowerShell:

```powershell
Set-Location .\frontend
Copy-Item .env.example .env
pnpm install
pnpm build
pnpm dev
```

La aplicación queda en `http://localhost:5173`. La variable `VITE_API_URL` de `frontend/.env` apunta a `http://localhost:8000/api/v1`.

## Funcionalidades

- Registro e inicio de sesión de clientes.
- Catálogo con búsqueda y filtros.
- Carrito y confirmación de pedidos.
- Consulta y cancelación de pedidos propios pendientes.
- Administración de categorías, productos, stock, pedidos y usuarios.
- Cambios de estado de los pedidos e indicadores del negocio.
- Restitución del stock al cancelar un pedido.

## Entrega

El ZIP debe incluir `backend/`, `frontend/` y este `README.md` en la raíz. Excluir `.venv/`, `node_modules/` y los archivos `.env`. El video se entrega mediante el enlace público indicado arriba; no debe incluirse dentro del ZIP.