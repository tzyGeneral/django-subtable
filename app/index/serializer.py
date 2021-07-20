from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    name = serializers.CharField()
    gender = serializers.IntegerField()
