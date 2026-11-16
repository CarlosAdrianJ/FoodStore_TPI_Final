export type Role='admin'|'user'
export type OrderStatus='PENDIENTE'|'EN_PREPARACION'|'ENTREGADO'|'CANCELADO'
export interface User{id:number;username:string;full_name:string;email:string;role:Role;disabled:boolean;created_at:string}
export interface Category{id:number;nombre:string;descripcion:string|null;activo:boolean}
export interface Product{id:number;categoria_id:number;nombre:string;descripcion:string|null;precio_base:number;imagen_url:string|null;stock:number;disponible:boolean;activo:boolean;categoria?:Category}
export interface PageResult<T>{total:number;items:T[]}
export interface CartLine{product:Product;cantidad:number}
export interface OrderItem{producto_id:number;nombre_producto:string;precio_unitario:number;cantidad:number;subtotal:number}
export interface Order{id:number;usuario_id:number;estado:OrderStatus;forma_pago:'EFECTIVO'|'TRANSFERENCIA';direccion_entrega:string;notas:string|null;total:number;created_at:string;updated_at:string;items:OrderItem[]}
export interface Summary{pendientes:number;en_preparacion:number;entregados:number;cancelados:number;pedidos_hoy:number;ingresos_entregados:number}

export interface ProductInput{nombre:string;descripcion:string;precio_base:number;imagen_url:string;stock:number;disponible:boolean;categoria_id:number}
