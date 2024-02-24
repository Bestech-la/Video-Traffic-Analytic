from rest_framework import serializers
from apps.infraction_tracker.models import InfractionTracker


class InfractionTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfractionTracker
        fields = [
            "id",
            "video",
            "image_one",
            "image_two",
            "vehicle_registration_number",
            "brand",
            "vehicle_color",
            "vehicle_registration_color",
            "province",
            "created_on",
            "date_time",
            "algorithm",
        ]
