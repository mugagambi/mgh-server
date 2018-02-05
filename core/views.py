from django.shortcuts import render
from rest_framework import viewsets
from core import models
from core import serializers


# Create your views here.
class AggregationCenterViewSet(viewsets.ModelViewSet):
    queryset = models.AggregationCenter.objects.all()
    serializer_class = serializers.AggregationCenterSerializer
