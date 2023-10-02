from django_filters import rest_framework as filters
from datetime import datetime
from apps.infraction_tracker.models import InfractionTracker

class InfractionTrackerFilterSet(filters.FilterSet):
    id = filters.AllValuesMultipleFilter(field_name='id')
    created_on = filters.CharFilter(method='filter_created_on')
    
    def filter_created_on(self, queryset, name, value):
        try:
            created_on_date = datetime.strptime(value, '%Y-%m-%d').date()
            return queryset.filter(created_on__date=created_on_date)
        except ValueError:
            return queryset.none()

    class Meta:
        model = InfractionTracker
        fields = ["id", "created_on",'vehicle_registration_number']
