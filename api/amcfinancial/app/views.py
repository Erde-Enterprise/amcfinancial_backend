from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import base64
import os

from .models import User_Root, Customer
from .serializers import AccessSerializer, LoginSerializer, RegisterCostumerSerializer
from .middleware import teste_token
from drf_spectacular.utils import extend_schema, OpenApiParameter
class ValidateTokenView(APIView):
  @extend_schema(
    summary="Validates User Token API",
    description="Validates the authenticity of a user token received in the request data.",
    parameters=[OpenApiParameter(
      name="access_token", 
      description="User access token to be validated", 
      required=True, type=str,
      location="query")],
    request=AccessSerializer,
    responses={
      200: {
        "description": "Successful token validation.", 
        "content": {
            "application/json": {
              "example": {
                "response": "Valid token"}}}},
      400: {
        "description": "Invalid token or Activation Expired.", 
        "content": {
            "application/json": {
                "example": {
                    "error": "Invalid token or Activation Expired"}}}},
      500: {
        "description": "Internal Server Error.", 
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error"}}}}
    }
  )
  
  def post(self, request): 
    try:
      serializer = AccessSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      token = serializer.validated_data['access_token']
      validation = teste_token(token)
      if validation['validity']:
          return Response({'response':'Valid token'}, status=status.HTTP_200_OK)
      else:
          return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    def post(self, request):
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
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_nickname = serializer.validated_data['email_or_nickname']
        password = serializer.validated_data['password']

        user_root = User_Root.objects.filter(Q(email_root=email_or_nickname) | Q(nickname=email_or_nickname)).first()
        if user_root and check_password(password, user_root.password):
            image_binary_data = user_root.photo
            image_base64 = base64.b64encode(image_binary_data).decode('utf-8') 
            refresh = RefreshToken.for_user(user_root)
            refresh['type'] = 0
            return Response({'token': str(refresh),
                            'email': user_root.email_root,
                            'nickname': user_root.nickname,
                            'name': user_root.name,
                            'photo': image_base64,
                            'user_type': 0}, status=status.HTTP_200_OK)
        
        customer = Customer.objects.filter(Q(email=email_or_nickname) | Q(nickname=email_or_nickname)).first() 
        if customer and check_password(password, customer.password):
            image_binary_data = customer.photo
            image_base64 = base64.b64encode(image_binary_data).decode('utf-8') 
            refresh = RefreshToken.for_user(customer)
            refresh['type'] =customer.type
            return Response({'token': str(refresh),
                            'email': customer.email,
                            'nickname': customer.nickname,
                            'name': customer.name,
                            'photo': image_base64,
                            'user_type': customer.type}, status=status.HTTP_200_OK)
        
        return Response({'is_valid': False,}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterCustomerView(APIView):
    def post(self, request):
        """
        Register Customer API.

        Registers a new customer account.
        
        ---
        parameters:
          - access_token: Access token for authentication.
            - required: true
            - type: string
          - name: User's name.
            - required: true
            - type: string
          - nickname: User's nickname.
            - required: true
            - type: string
          - email: User's email address.
            - required: true
            - type: string
          - password: User password.
            - required: true
            - type: string
          - photo: User's profile photo (optional).
            - required: false
            - type: file
          - type: Type of customer (1 or 2).
            - required: true
            - type: integer 
            \n
        responses:
          - 200: Successful registration - Returns a success message.
            - response: Success message indicating the user has been created.
              - type: string
          - 400: Bad request. Invalid token or missing/invalid parameters.
            - error: Error message indicating the issue.
              - type: string
          - 401: Unauthorized. Invalid access token.
            - error: Error message indicating the issue.
              - type: string
          - 400: Bad request. User with this email/nickname already exists.
            - error: Error message indicating the issue.
              - type: string
          - 500: Internal Server Error.
            - error: Error message indicating the issue.
              - type: string
        """
        try:
            serializer = RegisterCostumerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validation = teste_token(serializer.validated_data['access_token'])
            if validation['validity']:
                if validation['type'] == 0:
                    userRoot = User_Root.objects.get(id=validation['id'])
                    if 'photo' in request.FILES and request.FILES['photo']:
                        photo_bytes = request.FILES['photo'].read()
                    else:
                        current_directory = os.path.dirname(os.path.abspath(__file__))
                        avatar_path = os.path.join(current_directory, 'static/images/avatar.png')
                        with open(avatar_path, 'rb') as f:
                            photo_bytes = f.read()
                    password_crypt = make_password(serializer.validated_data['password'])
                    customer = Customer.objects.create(
                        name=serializer.validated_data['name'],
                        nickname=serializer.validated_data['nickname'],
                        email=serializer.validated_data['email'],
                        password=password_crypt,
                        photo=photo_bytes,
                        type=serializer.validated_data['type'],
                        root=userRoot
                    ) 
                    customer.save()
                    return Response({'response': 'User created'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
