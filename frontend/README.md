# Food Store - Frontend

Aplicación React + TypeScript + Vite con Tailwind CSS.

## Requisitos
- Node.js 20.19 o superior
- pnpm 9 o superior
- Backend iniciado en http://localhost:8000

## Configuración
Copiar .env.example como .env. La URL predeterminada es http://localhost:8000/api/v1.

## Ejecutar
Desde la carpeta frontend:
1. pnpm install
2. pnpm dev
3. Abrir http://localhost:5173

Para compilar: pnpm build

## Incluye
Registro e inicio de sesión OAuth2 con cookie HttpOnly; catálogo paginado con búsqueda y categoría; carrito persistido; checkout; consulta y cancelación de pedidos; rutas de administración; resumen, categorías, productos, pedidos y usuarios.
Axios usa withCredentials. No se lee ni se guarda el JWT en el navegador. TanStack Query gestiona los datos del servidor, TanStack Form los formularios, TanStack Table las tablas y Zustand persist el estado del cliente.
