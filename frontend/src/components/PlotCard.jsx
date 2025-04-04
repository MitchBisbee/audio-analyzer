import React from "react";
import PlotWrapper from "./PlotWrapper";
import { useRef } from "react";
import DashboardCard from "./DashboardCard";
import { Line } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register chart.js modules (necessary in Chart.js v3)
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Audio Plot",
    },
  },
};
const blueLineStyle = {
  borderColor: 'blue',
  backgroundColor: 'rgba(0, 0, 255, 0.1)', // Light blue fill (optional)
  pointRadius: 0 // cleaner look for audio plots
};

const enhanceWithStyle = (plot) => {
  const styled = {
    ...plot,
    datasets: plot.datasets.map(ds => ({
      ...ds,
      ...blueLineStyle,
    }))
  };
  return styled;
};

const PlotCard = ({frequencyResponseData, timeDomainResponseData,impulseResponseData}) => {
  const chartRef = useRef(null);
  if (!frequencyResponseData || !timeDomainResponseData || !impulseResponseData) {
    return <div style={{ textAlign: "center", padding: "1rem" }}><>🌀</>Loading plots...</div>;
  }
  const downLoadChart = () =>{
    const chart = chartRef.current;
    if (!chart) return;
    const url = chart.toBase64Image();
    const link = document.createElement("a");
    link.href = url;
    link.download = "audio_plot.png";
    link.click();
  }

  return (
    <DashboardCard title="📈 Plot Viewer">
      <PlotWrapper>
        <Line 
          ref = {chartRef} 
          data= {enhanceWithStyle(frequencyResponseData)} 
          options={options}
        />
      </PlotWrapper>

      <PlotWrapper>
        <Line
          ref = {chartRef}  
          data={enhanceWithStyle(timeDomainResponseData)} 
          options={options} 
        />
      </PlotWrapper>
      
      <PlotWrapper>
        <Line
          ref = {chartRef}  
          data={enhanceWithStyle(impulseResponseData)} 
          options={options}
        />
      </PlotWrapper>
      
      <button onClick={downLoadChart} style={{ marginTop: "1rem", 
        backgroundColor: "hsl(205, 100.00%, 50.00%)",
        color: "white",
        padding: "10px 20px",
        borderRadius: "5px",
        border: "none",
        cursor: "pointer",
        margin: "5px"}}>
        Download Frequency Plot PNG
      </button>
    </DashboardCard>
  );
};

export default PlotCard;