import React from "react";
import DashboardCard from "./DashboardCard";
import { ButtonTwo } from "../Buttons";
import "../App.css"

function PlaybackCard({playOriginalOnClick,playFilteredOnClick,
    pauseonClick,file}){
  
    return (
        <DashboardCard title={"Play Audio"}>
        <div className="button-container">
            <ButtonTwo
            name="▶️ Play Original"
            onClick={playOriginalOnClick}
            disabled={!file}
            />
            <ButtonTwo
            name="▶️ Play Filtered"
            onClick={playFilteredOnClick}
            disabled={!file}
            />
            <ButtonTwo
            name="⏸Pause"
            onClick={pauseonClick}
            disabled={!file}
            />
        </div>
        </DashboardCard>
    );
}
export default PlaybackCard;