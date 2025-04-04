import React from "react";

const PlotWrapper = ({ children }) => {
    return (
        <div style = {{width: "100%", maxWidth: "800px", margin: "2rem auto"}}>
            {children}
        </div>
    )
}

export default PlotWrapper;