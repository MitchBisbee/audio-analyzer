"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_audio, name="upload-audio"),
    path("filter/", views.apply_filter, name="apply-filter"),
    path("plot_waveform/", views.plot_waveform, name="plot-waveform"),
    path("get_audio/", views.get_audio_file, name="get-audio"),
    path("get_plot_data/", views.get_plot_data, name="get-plot-data")
]
