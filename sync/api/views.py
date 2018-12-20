from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import DataSerializer


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def sync_data(request, format=None):
    serializer = DataSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        data = serializer.validated_data
        print(data)
        return Response({'message': 'successfully synchronized'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
