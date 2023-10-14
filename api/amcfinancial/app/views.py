from .models import User_Root
from .serializers import UserRootSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_root(request):
    root = User_Root.objects.all()
    serializer = UserRootSerializer(root, many=True)
    return Response(serializer.data)