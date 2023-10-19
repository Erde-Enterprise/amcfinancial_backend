from .models import User_Root, Customer
from .serializers import UserRootSerializer, LoginSerializer, AccessSerializer
from django.db.models import Q
import jwt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

import sys
sys.path.append('..')
from amcfinancial.settings import SECRET_KEY


@api_view(['GET'])
def get_root(request):
    root = User_Root.objects.all()
    serializer = UserRootSerializer(root, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def teste_token(request):
    try:
        serializer = AccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['access_token']
        payload = jwt.decode(token,SECRET_KEY, algorithms=['HS256'])
        user = User_Root.objects.get(id=payload['user_id'])

        if user:
            serializer = UserRootSerializer(user)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
    except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_nickname = serializer.validated_data['email_or_nickname']
        password = serializer.validated_data['password']

        user_root = User_Root.objects.filter(Q(email_Root=email_or_nickname)|Q(nickname=email_or_nickname), password=password).first()

        if user_root:
            refresh = RefreshToken.for_user(user_root)
            return Response({'token': str(refresh),
                             'email': user_root.email_Root,
                             'nickname': user_root.nickname,
                             'name': user_root.name,
                             'photo': user_root.photo,
                             'user_type': 0}, status=status.HTTP_200_OK)
        
        customer = Customer.objects.filter(Q(email=email_or_nickname)|Q(nickname=email_or_nickname), password=password).first() 
        if customer:
            refresh = RefreshToken.for_user(customer)
            return Response({'token': str(refresh),
                             'email': customer.email,
                             'nickname': customer.nickname,
                             'name': customer.name,
                             'photo': customer.photo,
                             'user_type': customer.type}, status=status.HTTP_200_OK)
            
        return Response({'is_valid': False,}, status=status.HTTP_401_UNAUTHORIZED)