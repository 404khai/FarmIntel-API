from rest_framework import serializers


class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)


class SensorDataSerializer(serializers.Serializer):
    soil_moisture = serializers.FloatField(required=False)
    ph = serializers.FloatField(required=False)
    nitrogen = serializers.FloatField(required=False)
    phosphorus = serializers.FloatField(required=False)
    potassium = serializers.FloatField(required=False)
    temperature = serializers.FloatField(required=False)
    humidity = serializers.FloatField(required=False)


class FarmDataSerializer(serializers.Serializer):
    soil_type = serializers.CharField(required=True)
    crop_type = serializers.CharField(required=True)
    location = LocationSerializer(required=False)
    field_area_hectares = serializers.FloatField(required=False)
    sensor_data = SensorDataSerializer(required=False)
