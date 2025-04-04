import logging
from dataclasses import dataclass, field, asdict
from typing import List
import numpy as np
import scipy.constants
import scipy.io.wavfile
import scipy.signal
import matplotlib.pyplot as plt
from enum import Enum
import io
import base64
import sounddevice as sd

# need to adjust some things so that the dtft of music files can be plotted
# then this should be ready to be used as a backend for the audio app
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PlotType(Enum):
    LINE = "line"
    BAR = "bar"
    AREA = "area"
    SCATTER = "scatter" 

@dataclass
class PlotData:
    x_axis: List[float] = field(default_factory=list)
    y_axis: List[float] = field(default_factory=list)
    x_label: str = ""
    y_label: str = ""
    title: str = ""
    plot_type: PlotType = PlotType.LINE  # default is line plot

    def peak_preserving_downsample(self, max_points=2000):
        if len(self.x_axis) <= max_points:
            return self.x_axis, self.y_axis

        bucket_size = len(self.x_axis) // (max_points // 2)
        x_ds, y_ds = [], []

        for i in range(0, len(self.x_axis), bucket_size):
            x_chunk = self.x_axis[i:i + bucket_size]
            y_chunk = self.y_axis[i:i + bucket_size]
            if len(x_chunk) == 0:
                continue
            y_min = np.min(y_chunk)
            y_max = np.max(y_chunk)
            idx_min = np.argmin(y_chunk)
            idx_max = np.argmax(y_chunk)

            if idx_min < idx_max:
                x_ds.extend([x_chunk[idx_min], x_chunk[idx_max]])
                y_ds.extend([y_min, y_max])
            else:
                x_ds.extend([x_chunk[idx_max], x_chunk[idx_min]])
                y_ds.extend([y_max, y_min])

        return np.array(x_ds), np.array(y_ds)

    def to_chartjs(self, max_points=2000):
        x_ds, y_ds = self.peak_preserving_downsample(max_points)
        return {
            "labels": list(x_ds),
            "datasets": [{
                "label": self.title or "Plot",
                "data": list(y_ds),
                "type": self.plot_type.value,  # chart.js supports per-dataset type
                "fill": self.plot_type == PlotType.AREA
            }]
        }

class AudioAnalyzer:
    def __init__(self, filename):
        try:
            self.sr, self.y = scipy.io.wavfile.read(filename)
            self.filtered_signal = None
            self.filename = filename
            self.plot_data = {
                "filter_frequency_response": PlotData(),
                "filter_impulse_response": PlotData(),
                "filter_time_domain_response": PlotData()
            }
        except Exception as e:
            logging.error(f"Failed to load audio file {filename}: {e}")
            raise IOError(f"Could not read file {filename}: {e}")

    def apply_bandpass_filter(self, lowcut, highcut, order):
        try:
            sos = scipy.signal.butter(
                order, [lowcut, highcut], btype='band', fs=self.sr, output='sos')
            self.filtered_signal = scipy.signal.sosfilt(sos, self.y)
        except ValueError as e:
            logging.error("Error applying bandpass filter: %s", e)
            raise

    def apply_highpass_filter(self, order, cutoff):
        try:
            w_n = cutoff / (self.sr/2)
            sos = scipy.signal.butter(
                N=order, Wn=w_n, btype='high', fs=self.sr, output='sos')
            self.filtered_signal = scipy.signal.sosfilt(sos, self.y)
        except ValueError as e:
            logging.error("Error applying highpass filter: %s", e)
            raise

    def apply_lowpass_filter(self, cutoff, order):
        try:
            w_n = cutoff / (self.sr/2)
            sos = scipy.signal.butter(
                order, Wn=w_n, btype='low', fs=self.sr, output='sos')
            self.filtered_signal = scipy.signal.sosfilt(sos, self.y)
        except ValueError as e:
            logging.error("Error applying lowpass filter: %s", e)
            raise

    def apply_bandstop_filter(self, cutoff: tuple, order: int):
        try:
            if not isinstance(cutoff, tuple) or len(cutoff) != 2:
                raise ValueError(
                    "Cutoff must be a tuple (low_freq, high_freq)")
            sos = scipy.signal.butter(
                order, cutoff, btype='bandstop', fs=self.sr, output='sos')
            self.filtered_signal = scipy.signal.sosfilt(sos, self.y)
        except ValueError as e:
            logging.error("Error applying bandstop filter: %s", e)
            raise

    def apply_fourier_transform(self):
        try:
            fft = np.fft.fft(self.y)
            return fft
        except Exception as e:
            logging.error("Error computing Fourier Transform: %s", e)
            raise

    def display_filter_frequency_response(self, filter_type, order, cutoff, display=False):
        # Displays the frequency response of a filter
        w_n = cutoff / (self.sr / 2)
        if filter_type.lower() == "high":
            b, a = scipy.signal.butter(
                order, Wn=w_n, btype="high", output='ba')
        elif filter_type.lower() == "low":
            b, a = scipy.signal.butter(order, Wn=w_n, btype="low", output='ba')
        elif filter_type.lower() == "band":
            if not isinstance(cutoff, tuple):
                raise ValueError(
                    "Cutoff for 'band' type must be a tuple (low, high)")
            b, a = scipy.signal.butter(
                order, Wn=cutoff, btype="band", fs=self.sr, output='ba')
        elif filter_type.lower() == "bandstop":
            if not isinstance(cutoff, tuple):
                raise ValueError(
                    "Cutoff for 'bandstop' type must be a tuple (low, high)")
            b, a = scipy.signal.butter(
                order, Wn=cutoff, btype="bandstop", fs=self.sr, output='ba')
        else:
            raise ValueError(
                "filter_type must be 'high', 'low', 'band', or 'bandstop'")
        w, h = scipy.signal.freqz(b, a)
        x = w * \
            self.sr / (2 * np.pi)
        y = np.abs(h)

        self.plot_data["filter_frequency_response"].x_axis = x
        self.plot_data["filter_frequency_response"].y_axis = y
        self.plot_data["filter_frequency_response"].x_label = "Frequency (Hz)"
        self.plot_data["filter_frequency_response"].y_label = "Magnitude"
        self.plot_data["filter_frequency_response"].title = f"{filter_type} pass filter response"

        if display:
            self._plot(f"{filter_type} pass filter response",
                       x=x, y=y, x_label="Frequency (Hz)", y_label="Magnitude")

    def display_filter_impulse_response(self, filter_type, order, cutoff, display=False):
        # Displays the impulse response of a filter using the length of the audio data
        try:
            # Calculate normalized cutoff frequency or frequencies
            w_n = cutoff / (self.sr / 2) if isinstance(cutoff,
                                                       (int, float)) else np.array(cutoff) / (self.sr / 2)
            # Design the filter based on type and cutoff
            if filter_type.lower() == "high":
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="high", output='ba')
            elif filter_type.lower() == "low":
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="low", output='ba')
            elif filter_type.lower() == "band":
                if not isinstance(cutoff, tuple):
                    raise ValueError(
                        "Cutoff for 'band' type must be a tuple (low, high)")
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="band", fs=self.sr, output='ba')
            elif filter_type.lower() == "bandstop":
                if not isinstance(cutoff, tuple):
                    raise ValueError(
                        "Cutoff for 'bandstop' type must be a tuple (low, high)")
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="bandstop", fs=self.sr, output='ba')
            else:
                raise ValueError(
                    "filter_type must be 'high', 'low', 'band', or 'bandstop'")

            # Generate an impulse signal with the same length as the audio data
            impulse = np.zeros(len(self.y))
            impulse[0] = 1  # Creating an impulse at the start
            # Compute the filter's response to the impulse
            response = scipy.signal.lfilter(b, a, impulse)

            # Calculate the time array corresponding to each sample in the response
            time_array = np.arange(len(response)) / self.sr
            self.plot_data["filter_impulse_response"].x_axis = time_array
            self.plot_data["filter_impulse_response"].y_axis = response
            self.plot_data["filter_impulse_response"].x_label = "Time (seconds)"
            self.plot_data["filter_impulse_response"].y_label = "Amplitude"
            self.plot_data["filter_impulse_response"].title = f"Order: {order} {filter_type.capitalize()} Pass Filter - Impulse Response"

            # Plot the response
            if display:
                self._plot(f"Order: {order} {filter_type.capitalize()} Pass Filter - Impulse Response",
                           x=time_array, y=response, x_label="Time (seconds)", y_label="Amplitude")
        except ValueError as e:
            logging.error("Invalid filter parameters: %s", e)
            raise

    def display_filtered_audio(self, filter_type, order, cutoff, display=False):
        try:
            # Calculate normalized cutoff frequency or frequencies
            w_n = cutoff / (self.sr / 2) if isinstance(cutoff,
                                                       (int, float)) else np.array(cutoff) / (self.sr / 2)
            # Design the filter based on type and cutoff
            if filter_type.lower() == "high":
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="high", output='ba')
            elif filter_type.lower() == "low":
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="low", output='ba')
            elif filter_type.lower() == "band":
                if not isinstance(cutoff, tuple):
                    raise ValueError(
                        "Cutoff for 'band' type must be a tuple (low, high)")
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="band", fs=self.sr, output='ba')
            elif filter_type.lower() == "bandstop":
                if not isinstance(cutoff, tuple):
                    raise ValueError(
                        "Cutoff for 'bandstop' type must be a tuple (low, high)")
                b, a = scipy.signal.butter(
                    order, Wn=w_n, btype="bandstop", fs=self.sr, output='ba')
            else:
                raise ValueError(
                    "filter_type must be 'high', 'low', 'band', or 'bandstop'")

            filt_speech = scipy.signal.lfilter(b, a, self.y)
            # Calculate the time array corresponding to each sample in the response
            time_array = np.arange(len(self.y)) / self.sr
            # fill the plot data
            self.plot_data["filter_time_domain_response"].x_axis = time_array
            self.plot_data["filter_time_domain_response"].y_axis = filt_speech
            self.plot_data["filter_time_domain_response"].x_label = "Time (seconds)"
            self.plot_data["filter_time_domain_response"].y_label = "Amplitude"
            self.plot_data["filter_time_domain_response"].title = f"Order: {order} {filter_type.capitalize()} Pass Filter - Time Domain Response"
            # Plot the response
            if display:
                self._plot(f"Order: {order} {filter_type.capitalize()} Pass Filter - Time Domain Response",
                           x=time_array, y=filt_speech, x_label="Time (seconds)", y_label="Amplitude")
        except ValueError as e:
            logging.error("Invalid filter parameters: %s", e)
            raise

    def display_spectral_content(self):
        # Display the spectral content of the audio
        f, t, Sxx = scipy.signal.spectrogram(self.y, self.sr)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx))
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Spectral Content of ' + self.filename)
        plt.colorbar(label='Intensity [dB]')
        plt.show()

    def display_norm_wave_content(self):
        # Display the normalized waveform of the audio and converts the plot
        # to an image string
        plt.plot(np.arange(len(self.y)) / self.sr,
                 self.y / np.max(np.abs(self.y)))
        print(self.filename)
        plt.title('Normalized Waveform')
        plt.xlabel('Time [seconds]')
        plt.ylabel('Amplitude [normalized]')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()
        return img_str

    def _plot(self, title, x, y, x_label, y_label):
        # Plots the frequency response of a filter
        plt.plot(x, y)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid()
        plt.show()

    def play_audio(self, filtered_signal=False):
        if filtered_signal:
            if self.filtered_signal is not None and filtered_signal.size > 0:
                sd.play(data=filtered_signal, samplerate=self.sr)
            else:
                raise ValueError(
                    "A filter must be applied before it can be played.")
        else:
            sd.play(data=self.y, samplerate=self.sr)

    def display_dtft_magnitude(self):
        # Plots the dtft magnitude of the file
        b, a = scipy.signal.freqz(self.y, 1, len(self.y), fs=self.sr)
        self._plot(f"DTFT Mag: {self.filename}", x=b, y=abs(
            a), x_label="Frequency (Hz)", y_label="Magnitude")

    def save_audio_file(self, use_filtered=True, output_filename=None):
        try:
            data_to_save = self.filtered_signal if use_filtered and self.filtered_signal is not None else self.y
            if output_filename is None:
                suffix = '_filtered' if use_filtered and self.filtered_signal is not None else '_original'
                output_filename = self.filename.replace(
                    '.wav', f'{suffix}.wav')
            scipy.io.wavfile.write(output_filename, self.sr, data_to_save)
            return output_filename
        except Exception as e:
            logging.error("Error saving audio file: %s", e)
            raise IOError("Failed to save file: %s", e)

    def to_serializable(self):
        return {
            "plot_data": {key: asdict(value) for key, value in self.plot_data.items()},
            "sample_rate": self.sr,
            "file": self.filename
        }
    
    def get_chartjs_data(self, max_points=2000):
        return {
            key: plot.to_chartjs(max_points)
            for key, plot in self.plot_data.items()
        }
