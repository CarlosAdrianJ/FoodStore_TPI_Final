import {create} from 'zustand'
import {persist} from 'zustand/middleware'
import type {CartLine,Product,User} from '../types'
interface AuthState{user:User|null;setUser:(user:User|null)=>void;clear:()=>void}
export const useAuth=create<AuthState>()(persist((set)=>({user:null,setUser:(user)=>set({user}),clear:()=>set({user:null})}),{name:'foodstore-auth',partialize:(state)=>({user:state.user})}))
interface CartState{items:CartLine[];add:(product:Product)=>void;remove:(id:number)=>void;quantity:(id:number,value:number)=>void;clear:()=>void}
export const useCart=create<CartState>()(persist((set)=>({
 items:[],
 add:(product)=>set((state)=>{const found=state.items.find((line)=>line.product.id===product.id);return found?{items:state.items.map((line)=>line.product.id===product.id?{...line,cantidad:Math.min(line.cantidad+1,product.stock)}:line)}:{items:[...state.items,{product,cantidad:1}]} }),
 remove:(id)=>set((state)=>({items:state.items.filter((line)=>line.product.id!==id)})),
 quantity:(id,value)=>set((state)=>({items:state.items.map((line)=>line.product.id===id?{...line,cantidad:Math.max(1,Math.min(value,line.product.stock))}:line)})),
 clear:()=>set({items:[]})
}),{name:'foodstore-cart'}))
