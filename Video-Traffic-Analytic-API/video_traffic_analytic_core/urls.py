from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Video Traffic Analytic",
        default_version='v1',
        description="Lucky Draw API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=[permissions.IsAuthenticated],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', (schema_view.with_ui('swagger',
         cache_timeout=0)), name='schema-swagger-ui'),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path('', include('apps.user.api.v1.urls'), name='user'),
    path('', include('apps.video.api.v1.urls'), name='video'),
    path('', include('apps.infraction_tracker.api.v1.urls'), name='infraction_tracker'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
