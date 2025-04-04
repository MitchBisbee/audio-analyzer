import React from "react";
import DashboardCard from "./DashboardCard";

function MetadataCard({metadata}){
    if (!metadata) return null;

    const {filename,duration,sample_rate,channels} = metadata;

    return(
        <DashboardCard title = {"File Data"}>
            <p><strong>Filename:</strong> {filename}</p>
            <p><strong>Duration:</strong> {duration} seconds</p>
            <p><strong>Sample Rate:</strong> {sample_rate} Hz</p>
            <p><strong>Channels:</strong> {channels}</p>
        </DashboardCard>
    )
}
export default MetadataCard;