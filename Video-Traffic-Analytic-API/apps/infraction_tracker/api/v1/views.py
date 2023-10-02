
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import InfractionTrackerSerializer
from apps.infraction_tracker.models import InfractionTracker
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django_filters.rest_framework import DjangoFilterBackend
from .filter import InfractionTrackerFilterSet

class ListCreateAPIView(ListCreateAPIView):
    queryset = InfractionTracker.objects.all()
    serializer_class = InfractionTrackerSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InfractionTrackerFilterSet

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "created_on",
                openapi.IN_QUERY,
                description="Filter by the date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ]
    )

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
     
class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = InfractionTracker.objects.all()
    serializer_class = InfractionTrackerSerializer
    parser_classes = (MultiPartParser, FormParser)
