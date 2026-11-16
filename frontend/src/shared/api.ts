import axios from 'axios'
import type {Category,Order,OrderStatus,PageResult,Product,ProductInput,Summary,User} from '../types'
import {useAuth} from './store'
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1',withCredentials:true})
api.interceptors.response.use(response=>response,error=>{if(axios.isAxiosError(error)&&error.response?.status===401)useAuth.getState().clear();return Promise.reject(error)})
export function message(error:unknown):string{
 if(axios.isAxiosError<{detail?:string|{msg?:string}[]}>(error)){const d=error.response?.data?.detail;if(typeof d==='string')return d;if(Array.isArray(d))return d.map(x=>x.msg||'Dato inválido').join(', ');if(error.code==='ERR_NETWORK')return 'No se pudo conectar con el backend. Iniciá el servidor y volvé a intentar.'}
 return 'Ocurrió un error. Intentá nuevamente.'
}
export const auth={
 me:async()=> (await api.get<User>('/auth/me')).data,
 login:async(username:string,password:string)=>{const form=new URLSearchParams({username,password});return (await api.post('/auth/token',form,{headers:{'Content-Type':'application/x-www-form-urlencoded'}})).data},
 register:async(data:{username:string;full_name:string;email:string;password:string})=>(await api.post<User>('/auth/register',data)).data,
 logout:async()=>api.post('/auth/logout')
}
export const categories={
 list:async()=> (await api.get<Category[]>('/categorias')).data,
 create:async(data:{nombre:string;descripcion:string})=>(await api.post<Category>('/categorias',data)).data,
 update:async(id:number,data:{nombre:string;descripcion:string})=>(await api.put<Category>('/categorias/'+id,data)).data,
 remove:async(id:number)=>api.delete('/categorias/'+id)
}
export const products={
 list:async(params:{skip?:number;limit?:number;search?:string;categoria_id?:number})=>(await api.get<PageResult<Product>>('/productos',{params})).data,
 create:async(data:ProductInput)=>(await api.post<Product>('/productos',data)).data,
 update:async(id:number,data:Partial<ProductInput>)=>(await api.put<Product>('/productos/'+id,data)).data,
 stock:async(id:number,data:{stock:number;disponible:boolean})=>(await api.patch<Product>('/productos/'+id+'/stock',data)).data,
 remove:async(id:number)=>api.delete('/productos/'+id)
}
export const orders={
 list:async(params:{skip?:number;limit?:number;estado?:OrderStatus})=>(await api.get<PageResult<Order>>('/pedidos',{params})).data,
 create:async(data:{items:{producto_id:number;cantidad:number}[];forma_pago:string;direccion_entrega:string;notas:string})=>(await api.post<Order>('/pedidos',data)).data,
 cancel:async(id:number)=>(await api.patch<Order>('/pedidos/'+id+'/cancelar')).data,
 change:async(id:number,estado:OrderStatus)=>(await api.patch<Order>('/pedidos/'+id+'/estado',{estado})).data,
 summary:async()=>(await api.get<Summary>('/pedidos/resumen')).data
}
export const users={
 list:async()=>(await api.get<User[]>('/admin/usuarios')).data,
 activate:async(id:number)=>api.post('/admin/usuarios/'+id+'/activar'),
 deactivate:async(id:number)=>api.post('/admin/usuarios/'+id+'/desactivar')
}
