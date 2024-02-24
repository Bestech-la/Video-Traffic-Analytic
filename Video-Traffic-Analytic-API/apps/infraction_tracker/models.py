from django.db import models
from sorl.thumbnail import ImageField
from django_cleanup.signals import cleanup_pre_delete
from sorl.thumbnail import delete
from  apps.video.models import Video

class InfractionTracker(models.Model):
    image_one = models.ImageField(
        verbose_name='ImageOne', upload_to='uploads/', blank=True, null=True
    )
    image_two = models.ImageField(
        verbose_name='ImageTwo', upload_to='uploads/', blank=True, null=True
    )
    vehicle_registration_number = models.CharField(
        max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    vehicle_color = models.CharField(max_length=255, blank=True, null=True)
    vehicle_registration_color = models.CharField(
        max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    algorithm = models.CharField(max_length=255, blank=True, null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "Infraction Tracker"
        verbose_name_plural = "Infraction Tracker"


def sorl_delete(**kwargs):
    delete(kwargs['file'])


cleanup_pre_delete.connect(sorl_delete)
