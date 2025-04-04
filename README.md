# 🎧 Audio Analyzer

A modern web-based audio analysis and visualization tool built with Django + React. Upload `.wav` files, apply digital filters, view waveform and filter response plots, and interact with your data in real-time.

---

## 🚀 Features

- Upload `.wav` audio files
- Visualize normalized waveform
- Apply digital filters: low-pass, high-pass, band-pass, band-stop
- View:
  - Frequency response
  - Impulse response
  - Time domain output
- Interactive plots using Chart.js
- Audio playback (original and filtered)
- Export plots as PNG
- Download filtered audio
- Responsive, modern UI with dark mode support

---

## 🛠 Tech Stack

### Frontend:
- [React](https://reactjs.org/)
- [Chart.js](https://www.chartjs.org/)
- `chartjs-plugin-zoom`
- CSS Flexbox layout
- Custom `DashboardCard` components

### Backend:
- [Django](https://www.djangoproject.com/)
- Django REST Framework
- NumPy, SciPy for audio signal processing
- Matplotlib (for waveform PNG export)

---

## 📦 Installation

### 🔧 Backend Setup

```bash
cd backend/
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 💻 Frontend Setup

```bash
cd frontend/
npm install
npm start
```

> 🧠 Note: On Windows or Node.js ≥17, you may need:
> ```bash
> set NODE_OPTIONS=--openssl-legacy-provider
> ```

---

## 🧪 Development Notes

- The app uses a two-column layout:
  - Left: Metadata, Filters, Controls
  - Right: Dynamic plot display
- Downsampling is peak-preserving to avoid flattening signal transients.
- The backend exposes endpoints to:
  - Upload audio
  - Apply filters
  - Generate plot data
  - Return filtered audio

---

## 🗂 Project Structure

```
/frontend
  └── src/
      ├── components/
      ├── App.js
      ├── api.js
      └── App.css

/backend
  └── analyzer/
      ├── views.py
      ├── utils/audio_analyzer.py
      └── serializers.py
```

---

## 🧑‍💻 Contributing

Coming soon. For now, feel free to fork and experiment.

---

## 📜 License

none at the moment

## 💡 Planned Features

✅ Export all plots at once  
✅ Play filtered audio in-browser  
✅ Improve download UX  
✅ Pressed-state animations for UI elements  
✅ Zoom & pan for waveforms

---

Built with 💙 by Mitch Bisbee
