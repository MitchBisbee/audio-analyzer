import React from "react";

function DashboardCard({ title, children }) {
    const cardStyle = {
      backgroundColor: "#1e1e1e",
      borderRadius: "10px",
      padding: "1rem",
      marginBottom: "1.5rem",
      boxShadow: "0 0 10px rgba(255,255,255,0.05)",
      width: "100%",
      boxSizing: "border-box",
      display: "flex",
      flexDirection: "column",
      alignItems: "stretch", // makes children fill horizontally
    };
  
    const titleStyle = {
      marginBottom: "0.5rem",
      fontSize: "16px",
      borderBottom: "1px solid #333",
      paddingBottom: "0.5rem"
    };
  
    return (
      <div style={cardStyle}>
        <div style={titleStyle}><strong>{title}</strong></div>
        <div style={{ width: "100%" }}>
          {children}
        </div>
      </div>
    );
  }
  
export default DashboardCard;