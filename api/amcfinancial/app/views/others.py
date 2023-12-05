from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..models import User_Root, Customer
from ..serializers import LoginSerializer, LoginCustomerResponseSerializer, LoginUserRootResponseSerializer

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

          user_root = User_Root.objects.filter(Q(email_root=email_or_nickname) | Q(nickname=email_or_nickname)).first()
          if user_root and check_password(password, user_root.password) and user_root.searchable:
              response = LoginUserRootResponseSerializer(user_root)
              return Response(response.data, status=status.HTTP_200_OK)
          
          customer = Customer.objects.filter(Q(email=email_or_nickname) | Q(nickname=email_or_nickname)).first() 
          if customer and check_password(password, customer.password) and customer.searchable:
              response = LoginCustomerResponseSerializer(customer)
              return Response(response.data, status=status.HTTP_200_OK)
          
          return Response({'error': 'Unauthorized User'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    