from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

import os

from ..models import User_Root, Customer
from ..serializers import RegisterCustomerSerializer, CustomerSerializer, ListCustomerSerializer
from ..middleware import teste_token

class RegisterCustomerView(APIView):
    @extend_schema(
        summary="Register Customer API",
        description="Registers a new customer account."
                    "Token received in the Authorization header.",
        request=RegisterCustomerSerializer,
        parameters=[
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
            201: {
                "description": "Successful registration - Returns a success message.",
                "example": {
                    "response": "User created"
                }
            },
            400: {
                "description": "Bad request. Missing/invalid parameters.",
                "example" : {
                    "error": "Bad request. Missing/invalid parameters."
                }
            },
            401: {
                "description": "Unauthorized. Invalid access token.",
                "example": {
                    "error": "Invalid token or Activation Expired"
                }
            },
            403: {
                "description": "Forbidden. Invalid user type.",
                "example": {
                    "error": "Invalid User Type"
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
            serializer = RegisterCustomerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validation = teste_token(request.headers)

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
                      return Response({'response': 'User created'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'error': 'User already exists'}, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'error': 'Integrity Error'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeleteCustomerView(APIView):
   @extend_schema(
       summary="Delete Customer API",
       description="Deletes a customer account."
                    "Token received in the Authorization header.",
       request=CustomerSerializer,
       parameters=[
           OpenApiParameter(
               name="nickname",
               description="User's nickname.",
               required=True,
               type=OpenApiTypes.STR,
               location="form",
           )
       ],
       responses={
           200: {
               "description": "Successful deletion - Returns a success message.",
               "example": {
                   "response": "Customer deleted successfully"
               }
           },
           400: {
               "description": "Bad request. Missing/invalid parameters.",
               "example": {
                   "error": "Bad request. Missing/invalid parameters."
               }
           },
           401: {
               "description": "Unauthorized. Invalid access token.",
               "example": {
                   "error": "Invalid token or Activation Expired"
               }
           },
           403: {
               "description": "Forbidden. Invalid user type.",
               "example": {
                   "error": "Invalid User Type"
               }
            },
            404: {
                "description": "Not Found. Customer not found.",
                "example": {
                    "error": "Customer not found"
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
   def delete(self,request):
    try:
      validation = teste_token(request.headers)
      serializer = CustomerSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      if validation['validity']:
            if validation['type'] == 0:
                customer = Customer.objects.get(nickname=serializer.validated_data['nickname'])
                customer.delete()
                return Response({"message": "Customer deleted successfully"}, status=status.HTTP_200_OK)
            else:
               return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
      else:
        return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except serializers.ValidationError as e:
      errors = dict(e.detail)  
      return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListCustomerView(APIView):
   def get(self, request):
        try:
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0:
                    customers = Customer.objects.all()
                    serializer = ListCustomerSerializer(customers, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)