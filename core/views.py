from rest_framework import viewsets
from core import models
from core import serializers


# Create your views here.
class AggregationCenterViewSet(viewsets.ModelViewSet):
    """
       retrieve:
       Return the given aggregation center.

       list:
       Return a list of all the existing aggregation centers.

       create:
       Create a new aggregation center instance.
       update:
       Update the given aggregation center
       """
    queryset = models.AggregationCenter.objects.all()
    serializer_class = serializers.AggregationCenterSerializer
