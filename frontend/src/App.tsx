import {useEffect} from 'react'
import {BrowserRouter,Navigate,NavLink,Outlet,Route,Routes} from 'react-router-dom'
import {QueryClient,QueryClientProvider,useQuery} from '@tanstack/react-query'
import {auth} from './shared/api'
import {useAuth} from './shared/store'
import {Layout} from './shared/layout'
import {Loading} from './shared/components'
import {Login,Register} from './features/auth/AuthPages'
import {CatalogPage} from './features/catalog/CatalogPage'
import {CartPage,CheckoutPage} from './features/cart/CartPages'
import {MyOrdersPage} from './features/orders/MyOrdersPage'
import {AdminHome,CategoriesAdmin,OrdersAdmin,ProductsAdmin,UsersAdmin} from './features/admin/AdminPages'

function Guard({admin=false}:{admin?:boolean}){
 const user=useAuth(state=>state.user)
 const setUser=useAuth(state=>state.setUser)
 const session=useQuery({queryKey:['me'],queryFn:auth.me,retry:false})
 useEffect(()=>{if(session.data)setUser(session.data);else if(session.isError)setUser(null)},[session.data,session.isError,setUser])
 if(session.isLoading&&!user)return <Loading/>
 if(!user)return <Navigate to="/login" replace/>
 if(admin&&user.role!=='admin')return <Navigate to="/unauthorized" replace/>
 return <Outlet/>
}
const queryClient=new QueryClient({defaultOptions:{queries:{staleTime:30000,refetchOnWindowFocus:false,retry:1},mutations:{retry:0}}})
function Router(){
 return <BrowserRouter><Routes>
  <Route element={<Layout/>}>
   <Route path="/" element={<CatalogPage/>}/>
   <Route path="/login" element={<Login/>}/>
   <Route path="/registro" element={<Register/>}/>
   <Route path="/carrito" element={<CartPage/>}/>
   <Route element={<Guard/>}>
    <Route path="/checkout" element={<CheckoutPage/>}/>
    <Route path="/mis-pedidos" element={<MyOrdersPage/>}/>
   </Route>
   <Route element={<Guard admin/>}>
    <Route path="/admin" element={<AdminHome/>}/>
    <Route path="/admin/categorias" element={<CategoriesAdmin/>}/>
    <Route path="/admin/productos" element={<ProductsAdmin/>}/>
    <Route path="/admin/pedidos" element={<OrdersAdmin/>}/>
    <Route path="/admin/usuarios" element={<UsersAdmin/>}/>
   </Route>
   <Route path="/unauthorized" element={<div className="p-12 text-center"><h1 className="text-3xl font-bold">Sin permiso</h1><NavLink className="text-blue-800" to="/">Volver al catálogo</NavLink></div>}/>
   <Route path="*" element={<Navigate to="/" replace/>}/>
  </Route>
 </Routes></BrowserRouter>
}
export default function App(){return <QueryClientProvider client={queryClient}><Router/></QueryClientProvider>}
