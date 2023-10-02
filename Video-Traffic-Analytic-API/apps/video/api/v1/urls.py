from django.urls import path
from .views import ListCreateAPIView, RetrieveUpdateDestroyAPIView

urlpatterns = [
    path('api/v1/video', ListCreateAPIView.as_view(), name='video'),
    path('api/v1/video/<int:pk>',
         RetrieveUpdateDestroyAPIView.as_view(), name='video'),
]
