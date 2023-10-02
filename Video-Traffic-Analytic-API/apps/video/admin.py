from django.contrib import admin
from .models import Video

class VideoAdmin(admin.ModelAdmin):
    list_display = ('yOne','yTwo', 'video',)
    
    fieldsets = (
        (None, {
            'fields': ('yOne','yTwo',  'video',)
        }),
    )

admin.site.register(Video, VideoAdmin)

