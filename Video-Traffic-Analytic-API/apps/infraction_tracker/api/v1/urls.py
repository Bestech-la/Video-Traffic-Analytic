from django.urls import path
from .views import ListCreateAPIView, RetrieveUpdateDestroyAPIView

urlpatterns = [
    path('api/v1/infraction_tracker', ListCreateAPIView.as_view(), name='infraction_tracker'),
    path('api/v1/infraction_tracker/<int:pk>',
         RetrieveUpdateDestroyAPIView.as_view(), name='infraction_tracker'),
]
