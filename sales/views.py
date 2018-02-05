from rest_framework import viewsets
from sales import serializers
from sales import models


# Create your views here.
class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
