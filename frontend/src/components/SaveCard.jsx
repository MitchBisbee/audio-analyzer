import React from "react";
import DashboardCard from "./DashboardCard";

function SaveCard({ downloadUrl }) {
  return (
    <DashboardCard title="💾 Save Filtered Audio">
      {downloadUrl ? (
        <a
          href={downloadUrl}
          download
          style={{
            display: "inline-block",
            padding: "10px 20px",
            backgroundColor: "hsl(140, 70%, 40%)",
            color: "white",
            borderRadius: "6px",
            textDecoration: "none"
          }}
        >
          Download Filtered Audio
        </a>
      ) : (
        <p style={{ color: "#aaa" }}>Apply a filter to enable download.</p>
      )}
    </DashboardCard>
  );
}

export default SaveCard;
