import React from "react";
import DashboardCard from "./DashboardCard";
import { ButtonTwo } from "../Buttons";


function PlaybackCard({playonClick,pauseonClick,file}){
  return(  <DashboardCard title={"Play Audio"}>
    <ButtonTwo 
        name = "▶️"
        onClick={playonClick} 
        disabled={!file} > 
    </ButtonTwo>

    <ButtonTwo 
        name = "⏸" 
        onClick={pauseonClick} 
        disabled={!file} > 
    </ButtonTwo>

    </DashboardCard>)

}
export default PlaybackCard;