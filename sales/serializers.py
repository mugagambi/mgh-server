from rest_framework import serializers
from sales import models


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ('name',)
