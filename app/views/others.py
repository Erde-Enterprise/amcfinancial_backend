from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

import pytz
from datetime import datetime

from ..models import User_Root, Customer, Access_History
from ..serializers import LoginSerializer, LoginCustomerResponseSerializer, LoginUserRootResponseSerializer, ListAccessHistorySerializer
from ..provides import  location_validation, get_or_create_user_profile
from ..middleware import teste_token

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
                    "photo": "/98uyoiwncs+9fd65df=fs5gfd",
                    "mime_type": "image/jpeg",
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
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']

            location = location_validation(latitude, longitude)
            timezone_switzerland = pytz.timezone('Europe/Zurich')

            user_root = User_Root.objects.filter(Q(email_root=email_or_nickname) | Q(nickname=email_or_nickname)).first()
            if user_root and check_password(password, user_root.password) and user_root.searchable:
                user = get_or_create_user_profile(user_root)
                access_history = Access_History.objects.create(
                    login_date = datetime.now(timezone_switzerland).date(),
                    login_time = datetime.now(timezone_switzerland).replace(microsecond=0).time(),
                    location = location['country'],
                    status = True,
                    user = user
                )
                access_history.save()
                response = LoginUserRootResponseSerializer(user_root)
                return Response(response.data, status=status.HTTP_200_OK)

            
            customer = Customer.objects.filter(Q(email=email_or_nickname) | Q(nickname=email_or_nickname)).first() 
            if customer and check_password(password, customer.password) and customer.searchable:
                user = get_or_create_user_profile(customer)
                access_history = Access_History.objects.create(
                    login_date = datetime.now(timezone_switzerland).date(),
                    login_time = datetime.now(timezone_switzerland).replace(microsecond=0).time(),
                    location = location['country'],
                    status = location['validation'],
                    user = user
                )
                access_history.save()
                if location['validation']:
                    response = LoginCustomerResponseSerializer(customer)
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
        
        except serializers.ValidationError as e:
            errors = dict(e.detail)  
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class ListAccessHistoryView(APIView):
    @extend_schema(
      summary="List Access History API",
      description="List all access history.",
      responses={
            200: {
                "description": "Successful request - Returns a list of access history.",
                "example": {
                            "user_nickname": "user123",
                            "login_date": "2022-01-01",
                            "login_time": "00:00:00",
                            "location": "Switzerland",
                            "status": True
                        }
                },
            401: {
                "description": "Unauthorized. Invalid token.",
                "example": {
                    "error": 'Unauthorized User'
                }
            },
            403: {
                "description": "Forbidden. Invalid user type.",
                "example": {
                    "error": 'Invalid User Type'
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
    def get(self, request):
        try:
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0:
                    access_history = Access_History.objects.filter(searchable=True)
                    serializer = ListAccessHistorySerializer(access_history, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
