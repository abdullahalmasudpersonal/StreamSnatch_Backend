from django.urls import path
from .views import download_media

urlpatterns = [
    path('download', download_media, name='download'),
]
