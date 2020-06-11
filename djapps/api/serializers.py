from rest_framework import serializers


class ThingSerializer(serializers.Serializer):
  text = serializers.CharField(max_length=200)
