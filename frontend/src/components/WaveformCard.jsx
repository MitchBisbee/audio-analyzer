import React from "react";
import DashboardCard from "./DashboardCard";

function WaveformCard({ file, waveformImage}) {
    return (
      <DashboardCard title="📈 Waveform Viewer">
       
        {waveformImage ? (
          <img
            src={waveformImage}
            alt="Waveform"
            style={{
              width: "100%",
              marginTop: "1rem",
              borderRadius: "8px",
              border: "1px solid #333"
            }}
          />
        ) : (
          <p style={{ marginTop: "1rem", color: "#aaa" }}>
            No waveform to display yet.
          </p>
        )}
      </DashboardCard>
    );
  }
  
  export default WaveformCard;