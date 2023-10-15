from .models import User_Root, Customer
from .serializers import UserRootSerializer, LoginSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_root(request):
    root = User_Root.objects.all()
    serializer = UserRootSerializer(root, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user_root = User_Root.objects.filter(email_Root=email, password=password).first()
        if user_root:

            return Response({'is_valid': True,
                             'user_type': 0}, status=status.HTTP_200_OK)
        
        customer = Customer.objects.filter(email=email, password=password).first()
        if customer:

            return Response({'is_valid': True,
                             'user_type': customer.type}, status=status.HTTP_200_OK)
        
        return Response({'is_valid': False,}, status=status.HTTP_401_UNAUTHORIZED)