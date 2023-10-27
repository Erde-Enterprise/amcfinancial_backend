from django.db.models import Q
import base64
import os
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User_Root, Customer
from .serializers import LoginSerializer, RegisterCostumerSerializer, AccessSerializer
from .middleware import teste_token

@api_view(['POST'])
def validate_token(request):
  """
  Validates User Token API.

  Validates the authenticity of a user token received in the request data.
  
  ---
  parameters:
    - access_token: User access token to be validated.
      - required: true
      - type: string
      \n
  responses:
    - 200: Successful token validation.
      - response: Indicates a valid token.
        - type: string
    - 400: Invalid token or Activation Expired.
      - error: Details about the error encountered during token validation.
        - type: string
    - 500: Internal Server Error.
      - error: Indicates a server-side error occurred during token validation.
        - type: string
  """
  try:
    serializer = AccessSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.validated_data['access_token']
    validation = teste_token(token)
    if validation['validity']:
      return Response({'response':'Valid token'}, status=status.HTTP_200_OK)
    else:
      return Response({'error': 'Invalid token or Activation Expired'}, status= status.HTTP_400_BAD_REQUEST)
  except:
      return Response({'error': 'Internal Server Error'}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login_view(request):
  """
  User Login API.

  Authenticates users based on provided email/nickname and password.
  
  ---
  parameters:
    - email_or_nickname: Email address or nickname of the user.
      - required: true
      - type: string 
    - password: User password.
        - required: true
        - type: string
      \n
  responses:
    - 200: Successful login - Returns user information and access token.
      - token: Access token for authenticated user.
        - type: string
      - email: User's email address.
        - type: string
      - nickname: User's nickname.
        - type: string
      - name: User's name.
        - type: string
      - photo: URL of user's profile photo.
        - type: string
      - user_type: Type of user (0 for User_Root, 1 for Customer type 1 and 2 for Customer type 2).
        - type: integer
    - 401: Unauthorized. Invalid credentials.
      - is_valid: Indicates if the login attempt is valid.
        - type: boolean
  """
  if request.method == 'POST':
      serializer = LoginSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      email_or_nickname = serializer.validated_data['email_or_nickname']
      password = serializer.validated_data['password']

      user_root = User_Root.objects.filter(Q(email_root=email_or_nickname)|Q(nickname=email_or_nickname), password=password).first()

      if user_root:
          image_binary_data = user_root.photo
          image_base64 = base64.b64encode(image_binary_data).decode('utf-8') 
          refresh = RefreshToken.for_user(user_root)
          return Response({'token': str(refresh),
                            'email': user_root.email_root,
                            'nickname': user_root.nickname,
                            'name': user_root.name,
                            'photo': image_base64,
                            'user_type': 0}, status=status.HTTP_200_OK)
      
      customer = Customer.objects.filter(Q(email=email_or_nickname)|Q(nickname=email_or_nickname), password=password).first() 
      if customer:
          image_binary_data = customer.photo
          image_base64 = base64.b64encode(image_binary_data).decode('utf-8') 
          refresh = RefreshToken.for_user(customer)
          return Response({'token': str(refresh),
                            'email': customer.email,
                            'nickname': customer.nickname,
                            'name': customer.name,
                            'photo': image_base64,
                            'user_type': customer.type}, status=status.HTTP_200_OK)
          
      return Response({'is_valid': False,}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register_costumer(request):
  try:
    serializer = RegisterCostumerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validation = teste_token(serializer.validated_data['access_token'])
    if validation['validity']:
      if validation['type'] == 0:
        userRoot = User_Root.objects.get(id=validation['id'])
        if request.FILES['photo']:
          photo_bytes = request.FILES['photo'].read()
        else:
          current_directory = os.path.dirname(os.path.abspath(__file__))
          avatar_path = os.path.join(current_directory, 'static/images/avatar.png')
          with open(avatar_path, 'rb') as f:
            photo_bytes = f.read()

        customer = Customer.objects.create(
        name = serializer.validated_data['name'],
        nickname = serializer.validated_data['nickname'],
        email = serializer.validated_data['email'],
        password = serializer.validated_data['password'],
        photo = photo_bytes,
        type = serializer.validated_data['type'],
        root = userRoot
        ) 
        customer.save()
        return Response({'response':'User created'}, status=status.HTTP_200_OK)
      else:
         return Response({'error': 'Unauthorized User'}, status= status.HTTP_401_UNAUTHORIZED)
    else:
      return Response({'error': 'Invalid token or Activation Expired'}, status= status.HTTP_400_BAD_REQUEST)
  except:
    return Response({'error': 'Internal Server Error'}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)