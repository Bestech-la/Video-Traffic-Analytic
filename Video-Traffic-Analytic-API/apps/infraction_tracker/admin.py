from django.contrib import admin
from .models import InfractionTracker


class InfractionTrackerAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle_registration_number",
        "brand",
        "vehicle_color",
        "vehicle_registration_color",
        "province",
        "image_one",
        "image_two",
        "video",
        "date_time",
        "algorithm",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "image_one",
                    "image_two",
                    "vehicle_registration_number",
                    "brand",
                    "vehicle_color",
                    "vehicle_registration_color",
                    "province",
                    "video",
                    "date_time",
                    "algorithm",
                )
            },
        ),
    )


admin.site.register(InfractionTracker, InfractionTrackerAdmin)
