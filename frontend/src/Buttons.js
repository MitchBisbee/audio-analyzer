import React from "react"
export function ButtonOne({name,onClick}){
    const styles = {
        backgroundColor: "hsl(205, 100.00%, 50.00%)",
        color: "white",
        padding: "10px 20px",
        borderRadius: "5px",
        border: "none",
        cursor: "pointer",
        display: "flex",
        justifyContent: "center"
    };
    return<button onClick = {onClick} style = {styles}>{name}</button>;
}


export function ButtonTwo({name,onClick,disabled}){
    const styles = {
        backgroundColor: "hsl(205, 100.00%, 50.00%)",
        color: "white",
        padding: "10px 20px",
        borderRadius: "5px",
        border: "none",
        cursor: "pointer",
        margin: "5px"
    };
    return<button onClick = {onClick} style = {styles} disbaled = {disabled}>{name}</button>;
}