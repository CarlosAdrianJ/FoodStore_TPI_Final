import {useMemo,useState} from 'react'
import {createColumnHelper} from '@tanstack/react-table'
import {useMutation,useQuery,useQueryClient} from '@tanstack/react-query'
import {useForm} from '@tanstack/react-form'
import {categories,orders,products,users,message} from '../../shared/api'
import type {Category,Order,OrderStatus,Product,ProductInput,User} from '../../types'
import {Alert,Button,Card,Field,Input,Table,Title,money} from '../../shared/components'

export function AdminHome(){
 const q=useQuery({queryKey:['summary'],queryFn:orders.summary})
 const entries=q.data?[['Pendientes',String(q.data.pendientes)],['En preparación',String(q.data.en_preparacion)],['Entregados',String(q.data.entregados)],['Cancelados',String(q.data.cancelados)],['Pedidos hoy',String(q.data.pedidos_hoy)],['Ingresos entregados',money(q.data.ingresos_entregados)]]:[]
 return <div><Title subtitle="Indicadores principales del negocio.">Panel de administración</Title><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{entries.map(([label,value])=><Card key={label}><p className="text-sm text-slate-500">{label}</p><b className="mt-2 block text-3xl text-blue-950">{value}</b></Card>)}</div><div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{[['/admin/categorias','Categorías'],['/admin/productos','Productos'],['/admin/pedidos','Pedidos'],['/admin/usuarios','Usuarios']].map(([href,label])=><a key={href} href={href} className="rounded-2xl border bg-white p-5 font-bold text-blue-950 shadow-sm">{label} →</a>)}</div></div>
}
export function CategoriesAdmin(){
 const [err,setErr]=useState('')
 const qc=useQueryClient()
 const q=useQuery({queryKey:['categories'],queryFn:categories.list})
 const create=useMutation({mutationFn:categories.create,onSuccess:()=>void qc.invalidateQueries({queryKey:['categories']}),onError:(e:unknown)=>setErr(message(e))})
 const update=useMutation({mutationFn:({id,data}:{id:number;data:{nombre:string;descripcion:string}})=>categories.update(id,data),onSuccess:()=>void qc.invalidateQueries({queryKey:['categories']}),onError:(e:unknown)=>setErr(message(e))})
 const remove=useMutation({mutationFn:categories.remove,onSuccess:()=>void qc.invalidateQueries({queryKey:['categories']}),onError:(e:unknown)=>setErr(message(e))})
 const form=useForm({defaultValues:{nombre:'',descripcion:''},onSubmit:async({value})=>{setErr('');await create.mutateAsync(value)}})
 const helper=createColumnHelper<Category>()
 const columns=useMemo(()=>[
  helper.accessor('nombre',{header:'Nombre'}),
  helper.accessor(row=>row.descripcion||'—',{id:'descripcion',header:'Descripción'}),
  helper.display({id:'acciones',header:'Acciones',cell:({row})=><div className="flex gap-3"><button className="font-semibold text-blue-800" onClick={()=>{const nombre=prompt('Nombre de la categoría',row.original.nombre);if(nombre===null)return;const descripcion=prompt('Descripción',row.original.descripcion||'');if(descripcion!==null)update.mutate({id:row.original.id,data:{nombre,descripcion}})}}>Editar</button><button className="font-semibold text-red-700" onClick={()=>{if(confirm('¿Dar de baja esta categoría?'))remove.mutate(row.original.id)}}>Baja</button></div>})
 ],[helper,remove,update])
 return <div><Title subtitle="Alta, modificación y baja lógica.">Administrar categorías</Title>{err&&<Alert>{err}</Alert>}<Card className="mb-5"><form className="grid gap-3 md:grid-cols-[1fr_2fr_auto]" onSubmit={event=>{event.preventDefault();void form.handleSubmit()}}><form.Field name="nombre">{field=><Field label="Nombre"><Input minLength={2} maxLength={100} value={field.state.value} onChange={event=>field.handleChange(event.target.value)} required/></Field>}</form.Field><form.Field name="descripcion">{field=><Field label="Descripción"><Input value={field.state.value} onChange={event=>field.handleChange(event.target.value)}/></Field>}</form.Field><Button disabled={create.isPending}>Crear categoría</Button></form></Card><Table data={q.data||[]} columns={columns}/></div>
}
export function ProductsAdmin(){
 const [err,setErr]=useState('')
 const qc=useQueryClient()
 const cats=useQuery({queryKey:['categories'],queryFn:categories.list})
 const q=useQuery({queryKey:['products','admin'],queryFn:()=>products.list({skip:0,limit:100})})
 const create=useMutation({mutationFn:products.create,onSuccess:()=>void qc.invalidateQueries({queryKey:['products']}),onError:(e:unknown)=>setErr(message(e))})
 const update=useMutation({mutationFn:({id,data}:{id:number;data:Partial<ProductInput>})=>products.update(id,data),onSuccess:()=>void qc.invalidateQueries({queryKey:['products']}),onError:(e:unknown)=>setErr(message(e))})
 const stock=useMutation({mutationFn:({id,value,available}:{id:number;value:number;available:boolean})=>products.stock(id,{stock:value,disponible:available}),onSuccess:()=>void qc.invalidateQueries({queryKey:['products']}),onError:(e:unknown)=>setErr(message(e))})
 const remove=useMutation({mutationFn:products.remove,onSuccess:()=>void qc.invalidateQueries({queryKey:['products']}),onError:(e:unknown)=>setErr(message(e))})
 const form=useForm({defaultValues:{nombre:'',descripcion:'',precio_base:0,imagen_url:'',stock:0,disponible:true,categoria_id:0},onSubmit:async({value})=>{setErr('');await create.mutateAsync(value)}})
 const helper=createColumnHelper<Product>()
 const columns=useMemo(()=>[
  helper.accessor('nombre',{header:'Producto'}),
  helper.accessor('precio_base',{header:'Precio',cell:cell=>money(cell.getValue())}),
  helper.accessor('stock',{header:'Stock'}),
  helper.accessor('disponible',{header:'Disponible',cell:cell=>cell.getValue()?'Sí':'No'}),
  helper.display({id:'acciones',header:'Acciones',cell:({row})=><div className="flex flex-wrap gap-2"><button className="font-semibold text-blue-800" onClick={()=>{const p=row.original;const nombre=prompt('Nombre',p.nombre);if(nombre===null)return;const precio=Number(prompt('Precio',String(p.precio_base)));const cantidad=Number(prompt('Stock',String(p.stock)));const categoria=Number(prompt('ID de categoría',String(p.categoria_id)));const descripcion=prompt('Descripción',p.descripcion||'');const imagen=prompt('URL de imagen',p.imagen_url||'');if(Number.isFinite(precio)&&precio>=0&&Number.isFinite(cantidad)&&cantidad>=0&&Number.isInteger(categoria)&&categoria>0&&descripcion!==null&&imagen!==null)update.mutate({id:p.id,data:{nombre,precio_base:precio,stock:cantidad,descripcion,imagen_url:imagen,disponible:p.disponible,categoria_id:categoria}})}}>Editar</button><button className="font-semibold text-amber-700" onClick={()=>{const p=row.original;const cantidad=Number(prompt('Nuevo stock',String(p.stock)));if(Number.isFinite(cantidad)&&cantidad>=0)stock.mutate({id:p.id,value:cantidad,available:confirm('¿Disponible para la venta?')})}}>Stock</button><button className="font-semibold text-red-700" onClick={()=>{if(confirm('¿Dar de baja este producto?'))remove.mutate(row.original.id)}}>Baja</button></div>})
 ],[helper,remove,stock,update])
 return <div><Title subtitle="Alta, modificación, stock, disponibilidad y baja lógica.">Administrar productos</Title>{err&&<Alert>{err}</Alert>}<Card className="mb-5"><h2 className="mb-4 font-bold">Nuevo producto</h2><form className="grid gap-3 md:grid-cols-2" onSubmit={event=>{event.preventDefault();void form.handleSubmit()}}>
  <form.Field name="nombre">{f=><Field label="Nombre"><Input value={f.state.value} onChange={event=>f.handleChange(event.target.value)} required/></Field>}</form.Field>
  <form.Field name="categoria_id">{f=><Field label="Categoría"><select className="rounded-xl border p-3" value={f.state.value} onChange={event=>f.handleChange(Number(event.target.value))} required><option value={0}>Elegí una categoría</option>{cats.data?.map(category=><option key={category.id} value={category.id}>{category.nombre}</option>)}</select></Field>}</form.Field>
  <form.Field name="precio_base">{f=><Field label="Precio"><Input type="number" min={0} step="0.01" value={f.state.value} onChange={event=>f.handleChange(Number(event.target.value))} required/></Field>}</form.Field>
  <form.Field name="stock">{f=><Field label="Stock"><Input type="number" min={0} value={f.state.value} onChange={event=>f.handleChange(Number(event.target.value))} required/></Field>}</form.Field>
  <form.Field name="descripcion">{f=><Field label="Descripción"><Input value={f.state.value} onChange={event=>f.handleChange(event.target.value)}/></Field>}</form.Field>
  <form.Field name="imagen_url">{f=><Field label="URL de imagen"><Input value={f.state.value} onChange={event=>f.handleChange(event.target.value)}/></Field>}</form.Field>
  <form.Field name="disponible">{f=><label className="flex items-center gap-2"><input type="checkbox" checked={f.state.value} onChange={event=>f.handleChange(event.target.checked)}/> Disponible para la venta</label>}</form.Field>
  <Button disabled={create.isPending}>Crear producto</Button>
 </form></Card><Table data={q.data?.items||[]} columns={columns}/></div>
}
export function OrdersAdmin(){
 const [err,setErr]=useState('')
 const qc=useQueryClient()
 const q=useQuery({queryKey:['orders','admin'],queryFn:()=>orders.list({skip:0,limit:100})})
 const change=useMutation({mutationFn:({id,status}:{id:number;status:OrderStatus})=>orders.change(id,status),onSuccess:()=>{void qc.invalidateQueries({queryKey:['orders']});void qc.invalidateQueries({queryKey:['summary']})},onError:(e:unknown)=>setErr(message(e))})
 const helper=createColumnHelper<Order>()
 const columns=useMemo(()=>[
  helper.accessor('id',{header:'N.º'}),
  helper.accessor('estado',{header:'Estado'}),
  helper.accessor('total',{header:'Total',cell:cell=>money(cell.getValue())}),
  helper.accessor('direccion_entrega',{header:'Dirección'}),
  helper.display({id:'estado_nuevo',header:'Cambiar estado',cell:({row})=><select className="rounded border p-2" value={row.original.estado} disabled={row.original.estado==='ENTREGADO'||row.original.estado==='CANCELADO'} onChange={event=>change.mutate({id:row.original.id,status:event.target.value as OrderStatus})}><option value="PENDIENTE">PENDIENTE</option><option value="EN_PREPARACION">EN_PREPARACION</option><option value="ENTREGADO">ENTREGADO</option><option value="CANCELADO">CANCELADO</option></select>})
 ],[change,helper])
 return <div><Title subtitle="Avanzá o cancelá pedidos según la máquina de estados.">Administrar pedidos</Title>{err&&<Alert>{err}</Alert>}<Table data={q.data?.items||[]} columns={columns}/></div>
}
export function UsersAdmin(){
 const [err,setErr]=useState('')
 const qc=useQueryClient()
 const q=useQuery({queryKey:['users'],queryFn:users.list})
 const change=useMutation({mutationFn:({id,disabled}:{id:number;disabled:boolean})=>disabled?users.deactivate(id):users.activate(id),onSuccess:()=>void qc.invalidateQueries({queryKey:['users']}),onError:(e:unknown)=>setErr(message(e))})
 const helper=createColumnHelper<User>()
 const columns=useMemo(()=>[
  helper.accessor('username',{header:'Usuario'}),helper.accessor('full_name',{header:'Nombre'}),helper.accessor('email',{header:'Email'}),helper.accessor('role',{header:'Rol'}),helper.accessor('disabled',{header:'Estado',cell:cell=>cell.getValue()?'Desactivado':'Activo'}),
  helper.display({id:'accion',header:'Acción',cell:({row})=><Button className={row.original.disabled?'bg-green-700':'bg-red-700'} onClick={()=>change.mutate({id:row.original.id,disabled:!row.original.disabled})}>{row.original.disabled?'Activar':'Desactivar'}</Button>})
 ],[change,helper])
 return <div><Title>Administrar usuarios</Title>{err&&<Alert>{err}</Alert>}<Table data={q.data||[]} columns={columns}/></div>
}
