from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from django.core.files.storage import default_storage
import os
from signaltools.audio_analyzer import AudioAnalyzer
from django.conf import settings


@api_view(["POST"])
def upload_audio(request):
    file = request.FILES.get("file")
    path = default_storage.save(file.name, file)
    full_path = default_storage.path(path)

    try:
        analyzer = AudioAnalyzer(full_path)
        duration = len(analyzer.y) / analyzer.sr

        return Response({
            "filename": file.name,
            "sample_rate": analyzer.sr,
            "duration": round(duration, 2),
            "channels": analyzer.y.shape[1] if analyzer.y.ndim > 1 else 1
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def apply_filter(request):
    try:
        # --- Input Extraction ---
        file = request.FILES.get("file")
        filter_type = request.data.get("filter_type")
        order = int(request.data.get("order", 2))
        cutoff = request.data.get("cutoff")

        # --- Cutoff Processing ---
        if "," in cutoff:
            cutoff_values = tuple(map(float, cutoff.split(",")))
        else:
            cutoff_values = float(cutoff)

        # --- Save Original File ---
        original_filename = default_storage.save(file.name, file)
        full_path = default_storage.path(original_filename)

        # --- Initialize Analyzer ---
        analyzer = AudioAnalyzer(full_path)

        # --- Apply Filter ---
        filter_type_lower = filter_type.lower()
        if filter_type_lower == "low":
            analyzer.apply_lowpass_filter(cutoff_values, order)
        elif filter_type_lower == "high":
            analyzer.apply_highpass_filter(order, cutoff_values)
        elif filter_type_lower == "band":
            lowcut = float(request.data.get("low cutoff"))
            highcut = float(request.data.get("high cutoff"))
            analyzer.apply_bandpass_filter(lowcut, highcut, order)
        elif filter_type_lower == "bandstop":
            lowcut = float(request.data.get("low cutoff"))
            highcut = float(request.data.get("high cutoff"))
            analyzer.apply_bandstop_filter((lowcut, highcut), order)
        else:
            return Response({"error": "Invalid filter type"}, status=400)

        # --- Generate New Filename ---
        base_name, _ = os.path.splitext(file.name)
        cutoff_str = (
            "-".join(map(str, cutoff_values))
            if isinstance(cutoff_values, tuple)
            else str(cutoff_values)
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
        new_filename = f"{base_name}_{filter_type_lower}_{cutoff_str}Hz_{timestamp}.wav"
        output_path = os.path.join(settings.MEDIA_ROOT, new_filename)

        # --- Save Filtered Audio ---
        filtered_path = analyzer.save_audio_file(
            use_filtered=True, output_filename=output_path
        )

        # --- Construct Download URL ---
        download_url = f"{settings.MEDIA_URL}{new_filename}"

        return Response(
            {
                "message": f"{filter_type} pass filter applied",
                "filter_file": new_filename,
                "download_url": download_url,
                "filtered_audio_url": download_url,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def plot_waveform(request):
    try:
        file = request.FILES.get("file")
        path = default_storage.save(file.name, file)
        full_path = default_storage.path(path)

        analyzer = AudioAnalyzer(full_path)
        img_str = analyzer.display_norm_wave_content()
        return Response({"image": img_str})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_audio_file(request):
    filename = request.GET.get("filename")

    if not filename:
        return Response({"error": "Filename is required as a query parameter."}, status=400)

    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if not os.path.exists(file_path):
        return Response({"error": "File not found."}, status=404)

    try:
        return FileResponse(open(file_path, "rb"), content_type="audio/wav")
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def get_plot_data(request):
    """Get plot data based on user input and return JSON-serializable plot information."""
    try:
        # --- Input Validation ---
        file = request.FILES.get("file")
        filter_type = request.data.get("filter_type")
        order = request.data.get("order", 2)
        cutoff = request.data.get("cutoff")
        print("this is my line ", file, filter_type, order, cutoff)
        print()
        # Check required parameters
        if not file or not filter_type or cutoff is None:
            return Response(
                {"error": "Missing one or more required parameters: file, filter_type, cutoff"},
                status=400
            )

        # --- Type Conversion ---
        try:
            order = int(order)
        except ValueError:
            return Response({"error": "Order must be an integer"}, status=400)

        # --- Cutoff Processing ---
        try:
            if "," in cutoff:
                cutoff = tuple(map(float, cutoff.split(",")))
            else:
                cutoff = float(cutoff)
        except ValueError:
            return Response({"error": "Cutoff must be a float or comma-separated floats"}, status=400)

        # --- File Handling ---
        path = default_storage.save(file.name, file)
        full_path = default_storage.path(path)
        # --- Analysis ---
        analyzer = AudioAnalyzer(full_path)
        analyzer.display_filter_frequency_response(
            filter_type=filter_type, order=order, cutoff=cutoff)

        analyzer.display_filter_impulse_response(
            filter_type=filter_type, order=order, cutoff=cutoff)
        analyzer.display_filtered_audio(
            filter_type=filter_type, order=order, cutoff=cutoff)
        # --- Return Data ---
        return Response({"plot_data": analyzer.get_chartjs_data()})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
