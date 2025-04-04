import React from "react";
import DashboardCard from "./DashboardCard";
import {ButtonTwo} from "../Buttons";

function FilterCard({file,filterType, setFilterType,cutoff, setCutoff, order, 
    setOrder,handleFilter, filteredMsg }){

        return(
            <DashboardCard title = "🎛️ Filter Controls">
                <label>Type:</label><br />
                <select value = {filterType} onChange={(e) => 
                    setFilterType(e.target.value)}
                    style={{ marginBottom: "0.5rem" }}>
                    <option value = "low">Low Pass</option>
                    <option value = "high">High Pass</option>
                    <option value = "band">Band Pass</option>
                    <option value = "bandstop">Band Stop</option>
                    </select><br />
                
                <label>Cutoff (Hz):</label><br />
                <input
                    value={cutoff}
                    onChange={(e) => setCutoff(e.target.value)}
                    placeholder="e.g. 500 or 300,3000"
                    style={{ width: "100%", marginBottom: "0.5rem" }}
                /><br />
                
                <label>Order:</label><br />
                <input 
                    type = "number"
                    value = {order}
                    onChange= {(e) => setOrder(e.target.value)}
                    style={{width: "100%", marginBottom: "0.5rem"}}
                />< br />
                <ButtonTwo 
                    name = "Apply Filter" 
                    onClick={handleFilter} 
                    disabled={!file} >
                </ButtonTwo>
                {filteredMsg && 
                <p 
                style={{ marginTop: "1rem", color: "lightgreen" }}
                >{filteredMsg}</p>}
            </DashboardCard>
        )
    }
export default FilterCard;