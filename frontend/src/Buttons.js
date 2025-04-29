import React from "react"
import "./App.css";
export function ButtonOne({name,onClick}){
    
    return<button onClick = {onClick} className = "button" >
           {name} 
          </button>;
}


export function ButtonTwo({name,onClick,disabled}){
    
    return <button onClick = {onClick} className="button" disbaled = {disabled}>
            {name}
           </button>;
}