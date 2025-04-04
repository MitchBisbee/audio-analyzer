from rest_framework.decorators import api_view
from rest_framework.response import Response
from dataclasses import asdict
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
        file = request.FILES.get("file")
        filter_type = request.data.get("filter_type")
        order = int(request.data.get("order", 2))
        cutoff = request.data.get("cutoff")
        if "," in cutoff:
            cutoff = tuple(map(float, cutoff.split(",")))
        else:
            cutoff = float(cutoff)

        path = default_storage.save(file.name, file)
        full_path = default_storage.path(path)

        analyzer = AudioAnalyzer(full_path)

        match filter_type.lower():
            case "low":
                analyzer.apply_lowpass_filter(cutoff, order)
            case "high":
                analyzer.apply_highpass_filter(order, cutoff)
            case "band":
                lowcut = request.data.get("low cutoff")
                highcut = request.data.get("high cutoff")
                analyzer.apply_bandpass_filter(lowcut, highcut, order)
            case "bandstop":
                lowcut = request.data.get("low cutoff")
                highcut = request.data.get("high cutoff")
                analyzer.apply_bandstop_filter((lowcut, highcut), order)
            case _:
                return Response({"error": "Invalid filter type"}, status=400)

        output_path = full_path.replace(".wav", "_filtered.wav")
        filtered_path = analyzer.save_audio_file(use_filtered=True,
                                                 output_filename=output_path)
        download_url = f"{settings.MEDIA_URL}{os.path.basename(filtered_path)}"
        return Response({
            "message": f"{filter_type} pass filter applied",
            "filter_file": os.path.basename(output_path),
            "download_url": download_url,
            "filtered_audio_url": download_url
        })
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
