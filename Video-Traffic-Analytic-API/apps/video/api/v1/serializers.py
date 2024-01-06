from rest_framework import serializers
from apps.video.models import Video

class VideoSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(write_only=True)
    class Meta:
        model = Video
        fields = ['yOne','yTwo',  'video', 'date_time']

    def create(self, validated_data):
        date_time = validated_data.pop('date_time', None)
        instance = super(VideoSerializer, self).create(validated_data)

        if date_time:
            instance.date_time = date_time
            instance.save()

        return instance