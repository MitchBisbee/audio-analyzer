import React, {useState,useRef,useEffect} from "react"
import './App.css';
import {uploadAudio, applyFilter, getAudioFile, getPlotData} from "./api";
import{ButtonOne} from "./Buttons.js";
import MetadataCard from "./components/MetadataCard";
import FilterCard from "./components/FilterCard";
import SaveCard from "./components/SaveCard";
import PlaybackCard from "./components/PlaybackCard";
import PlotCard from "./components/PlotCard";

//need the filter response plotted
// -need to make sure filter plot is being displayed after filter button is clicked - the plot data is being returned correctly from the backend, the next step is to render the plots - 4/1/2025
// -need the normalized wave form plotted when the dashboard is rendered
//need to add user authentication
function App() {
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [filterType, setFilterType] = useState("low");
  const [cutoff, setCutoff] = useState("");
  const [order, setOrder] = useState(2);
  const [filteredMsg, setFilteredMsg] = useState("");
  const [showDashboard, setShowDashboard] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);
  const [frequencyResponseData, setFrequencyResponseData] = useState(null);
  const [impulseResponseData, setImpulsResponseData] = useState(null);
  const [timeDomainResponseData, setTimeDomainResponseData] = useState(null);
  const [showFilterPlots, setShowFilterPlots] = useState(false);
  
  useEffect(() => {
    // Cleanup on unmount
    return () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }
    };
  }, []);


 const playAudio = async () => {
    try {
        if (!file || isPlaying) return;

        const data = await getAudioFile(file.name);
        const audio = new Audio(data);
        audioRef.current = audio;

        audio.addEventListener("ended", () => {
            setIsPlaying(false);
            audio.currentTime = 0;
        });

        audio.play();
        setIsPlaying(true);

    } catch (error) {
        console.error("Playback failed:", error);
    }
  };
  
  const playFilteredAudio = async () => {
    try{
      if(!downloadUrl || isPlaying) return;

        const response = await fetch(downloadUrl);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);

        const audio = new Audio(blobUrl);
        audioRef.current = audio;

        audio.addEventListener("ended", () => {
          setIsPlaying(false);
          audio.currentTime = 0;
        })
        audio.play();
        setIsPlaying(true);
    } catch (error){
      console.error("Filtered audio playback failed:", error);
    }
  }

  const pauseAudio = () => {
    try {
        if (!isPlaying || !audioRef.current) return;

        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setIsPlaying(false);
        audioRef.current = null;

    } catch (error) {
        console.error("Pause failed:", error);
    }
  };
  
  const handleUpload = async () => {
    try{
      const data = await uploadAudio(file);
      setMetadata(data);
      setShowDashboard(true);
    }
    catch (error){
      console.error("Upload failed: ", error);
    }
  };

  const handleFilter = async () => {
    try{
      const data = await applyFilter(file,filterType,cutoff,order);
      const plotData = await getPlotData(file,filterType,cutoff,order);
      setFrequencyResponseData(plotData["plot_data"]["filter_frequency_response"]);
      setTimeDomainResponseData(plotData["plot_data"]["filter_time_domain_response"]);
      setImpulsResponseData(plotData["plot_data"]["filter_impulse_response"]);
      setFilteredMsg(data.message);
      setDownloadUrl(`http://localhost:8000${data.download_url}`); //this needs work, the download is not working
      setShowFilterPlots(true);
    }
    catch(error){
      console.error("Filter failed:", error);
    }
  };

  const handleBack = async () => {
    setFile(null);
    setMetadata(null);
    setFilterType("low");
    setCutoff("");
    setOrder(2);
    setFilteredMsg("");
    setShowDashboard(false);
    setShowFilterPlots(false);
  }
  return (
    <div style={{ backgroundColor: "black", color: "white", minHeight: "100vh", padding: "2rem" }}>
      <h1 style={{ textAlign: "center" }}> <>🎧</> Audio Analyzer</h1>
  
      {!showDashboard ? (
        // 🔹 Upload View
        <>
          <div className="file-input-wrapper">
            <input
              type="file"
              accept=".wav"
              onChange={(e) => setFile(e.target.files[0])}
              className="file-input"
            />
          </div>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <ButtonOne name="Upload & Analyze" onClick={handleUpload} />
          </div>
        </>
      ) : (
        // 🔹 Dashboard View (Two Columns)
        <div className="dashboard-container">
          {/* Left Column */}
          <div className="left-column">
            <div className="dashboard-card">
              <MetadataCard metadata={metadata} />
            </div>
            
            <div className="dashboard-card">
              <PlaybackCard
                playOriginalOnClick={playAudio}
                playFilteredOnClick={playFilteredAudio}
                pauseonClick={pauseAudio}
                file={file}
              />
            </div>
  
            <div className="dashboard-card">
              <FilterCard
                file={file}
                filterType={filterType}
                setFilterType={setFilterType}
                cutoff={cutoff}
                setCutoff={setCutoff}
                order={order}
                setOrder={setOrder}
                handleFilter={handleFilter}
                filteredMsg={filteredMsg}
              />
            </div>
            
            <div className="dashboard-card">
              <SaveCard downloadUrl={downloadUrl} />
            </div>
  
            <div style={{ textAlign: "left", marginTop: "1rem" }}>
              <ButtonOne name="← Back" onClick={handleBack} />
            </div>
          </div>
  
          {/* Right Column */}
          <div className="right-column">
            <div className="dashboard-card">
            {showFilterPlots && (
              <PlotCard
                frequencyResponseData={frequencyResponseData}
                timeDomainResponseData={timeDomainResponseData}
                impulseResponseData={impulseResponseData}
              />
            )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default App;

