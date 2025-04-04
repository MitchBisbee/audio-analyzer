import axios from "axios";
import API_BASE from "./config";

export const uploadAudio = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(`${API_BASE}/upload/`, formData);
    return response.data;
};
  
export const applyFilter = async (file, filterType, cutoff, order) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("filter_type", filterType);
    formData.append("cutoff", cutoff);
    formData.append("order", order);
    const response = await axios.post(`${API_BASE}/filter/`, formData);
    return response.data;
};

export const getWaveformPlot = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(`${API_BASE}/plot_waveform/`, formData);
    return response.data;
};

export const getAudioFile = async (fileName) => {
    try {
      const response = await axios.get(`${API_BASE}/get_audio/?filename=${fileName}`, {
        responseType: 'blob',
      });
      const audioUrl = URL.createObjectURL(response.data);
      return audioUrl;
    } catch (error) {
      console.error("Error fetching audio file:", error);
    }
  };


export const getPlotData = async (file, filterType, cutoff, order) => {
  try{  
    const formData = new FormData();
    formData.append("file", file);
    formData.append("filter_type", filterType);
    formData.append("cutoff", cutoff);
    formData.append("order", order);
    const response = await axios.post(`${API_BASE}/get_plot_data/`, formData);
    return response.data;
  } catch (error){
    console.log(error);
  }
}