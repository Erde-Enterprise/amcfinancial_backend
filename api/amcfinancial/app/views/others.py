from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

import base64

from ..models import User_Root, Customer
from ..serializers import LoginSerializer
from ..middleware import teste_token



class ValidateTokenView(APIView):

  @extend_schema(
        summary="Validates User Token API",
        description="Validates the authenticity of a user token received in the Authorization header.",
        responses={
            200: {
                "description": "Successful token validation.",
                "example": {
                    "response": "Valid token"
                }
            },
            401: {
                "description": "Invalid token or Activation Expired.",
                "example": {
                    "error": "Invalid token or Activation Expired"
                }
            },
            500: {
                "description": "Internal Server Error.",
                "example": {
                    "error": "Internal Server Error"
                }
            }
        }
    )
  
  def get(self,request):
      try:
          validation = teste_token(request.headers)
          if validation['validity']:
              return Response({'response':'Valid token'}, status=status.HTTP_200_OK)
          else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
      except:
          return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    @extend_schema(
      summary="User Login API",
      description="Authenticates users based on provided email/nickname and password.",
        parameters=[
            OpenApiParameter(
                name="email_or_nickname",
                description="Email address or nickname of the user.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="password",
                description="User password.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
        ],
      request=LoginSerializer,
      responses={
            200: {
                "description": "Successful login - Returns user information and access token.",
                "example": {
                    "token": "access_token_string",
                    "email": "user@example.com",
                    "nickname": "user123",
                    "name": "John Doe",
                    "photo": "http://example.com/user.jpg",
                    "user_type": 1,
                }
            },
            400: {
                "description": "Bad Request. Invalid/missing email or nickname.",
                "example": {
                    "error": "Bad Request. Invalid/missing email or nickname."
                }
            },
            401: {
                "description": "Unauthorized. Invalid credentials.",
                "example": {
                    "error": 'Unauthorized User'
                  }
            },
            500: {
                "description": "Internal Server Error.",
                "example": {
                    "error": "Internal Server Error"
                }
            }
        },
    )
    def post(self, request):
        try:
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
          
          return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    