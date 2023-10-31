from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

import base64
import os

from .models import User_Root, Customer, Medical_Clinic, Invoice, Access_History
from .serializers import AccessSerializer, LoginSerializer, RegisterCostumerSerializer, RegisterClinicSerializer
from .middleware import teste_token


class ValidateTokenView(APIView):
  @extend_schema(
    summary="Validates User Token API",
    description="Validates the authenticity of a user token received in the request data.",
    parameters=[
        OpenApiParameter(
          name="access_token", 
          description="User access token to be validated", 
          required=True,
          type=OpenApiTypes.STR,
          location="form"
        )
    ],
    request=AccessSerializer,
    responses={
      200: {
        "description": "Successful token validation.", 
        "example": {
          "response": "Valid token"
        }
      },
      400: {
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
            401: {
                "description": "Unauthorized. Invalid credentials.",
                "example": {
                    "error": 'Unauthorized User'
                  }
            }
        },
    )
    def post(self, request):
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
        
        return Response({'is_valid': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
    
class RegisterCustomerView(APIView):
    @extend_schema(
        summary="Register Customer API",
        description="Registers a new customer account.",
        request=RegisterCostumerSerializer,
        parameters=[
            OpenApiParameter(
                name="access_token",
                description="Access token for authentication.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="name",
                description="User's name.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="nickname",
                description="User's nickname.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="email",
                description="User's email address.",
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
            OpenApiParameter(
                name="photo",
                description="User's profile photo (optional).",
                required=False,
                type=OpenApiTypes.BINARY,
                location="form",
            ),
            OpenApiParameter(
                name="type",
                description="Type of customer (1 or 2).",
                required=True,
                type=OpenApiTypes.NUMBER,
                location="form",
            ),
        ],
        responses={
            200: {
                "description": "Successful registration - Returns a success message.",
                "example": {
                    "response": "User created"
                }
            },
            400: {
                "description": "Bad request. Invalid token or missing/invalid parameters.",
                "example": {
                    "error": "Invalid token or Activation Expired"
                }
            },
            401: {
                "description": "Unauthorized. Invalid access token.",
                "example": {
                    "error": "Unauthorized User"
                }
            },
            409: {
                "description": "Conflict. User with this email/nickname already exists.",
                "example": {
                    "error": "User already exists"
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
    def post(self, request):
        try:
            serializer = RegisterCostumerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validation = teste_token(serializer.validated_data['access_token'])

            if validation['validity']:
                if validation['type'] == 0:
                    customer = Customer.objects.filter(Q(email=serializer.validated_data['email']) | Q(nickname=serializer.validated_data['nickname'])).first() 
                    userRoot = User_Root.objects.get(id=validation['id'])
                    if not customer:
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
                        return Response({'error': 'User already exists'}, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'error': 'Integrity Error'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RegisterClinicView(APIView):
     @extend_schema(
        summary="Register Clinic API",
        description="Registers a new clinic account.",
        request=RegisterClinicSerializer,
        parameters=[
            OpenApiParameter(
                name="access_token",
                description="Access token for authentication.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="name",
                description="Clinic's name.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="color",
                description="Clinic's color.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
        ],
        responses={
            200: {
                "description": "Successful registration - Returns a success message.",
                "example": {
                    "response": "Clinic created"
                }
            },
            400: {
                "description": "Bad request. Invalid token or missing/invalid parameters.",
                "example": {
                    "error": "Invalid token or Activation Expired"
                }
            },
            401: {
                "description": "Unauthorized. Invalid access token.",
                "example": {
                    "error": "Unauthorized User"
                }
            },
            409: {
                "description": "Conflict. Clinic with this name already exists.",
                "example": {
                    "error": "Clinic already exists"
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
     
     def post(self, request):
        try:  
          serializer = RegisterClinicSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          validation = teste_token(serializer.validated_data['access_token'])
          if validation['validity']:
              if validation['type'] == 0:
                  clinic = Medical_Clinic.objects.filter(name=serializer.validated_data['name']).first()
                  if not clinic:
                      clinic = Medical_Clinic.objects.create(
                          name=serializer.validated_data['name'],
                          color=serializer.validated_data['color'],
                      )
                      clinic.save()
                      return Response({'response': 'Clinic created'}, status=status.HTTP_200_OK)
                  else:
                      return Response({'error': 'Clinic already exists'}, status=status.HTTP_409_CONFLICT)
              else:
                  return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
          else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except:
          return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)