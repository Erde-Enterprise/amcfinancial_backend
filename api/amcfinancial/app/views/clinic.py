from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


from ..models import  Medical_Clinic
from ..serializers import  RegisterClinicSerializer, ListClinicSerializer, ClinicSerializer
from ..middleware import teste_token


class RegisterClinicView(APIView):
     @extend_schema(
        summary="Register Clinic API",
        description="Registers a new clinic account."
                    "Token received in the Authorization header.",
        request=RegisterClinicSerializer,
        parameters=[
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
            201: {
                "description": "Successful registration - Returns a success message.",
                "example": {
                    "response": "Clinic created"
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
          validation = teste_token(request.headers)
          if validation['validity']:
              if validation['type'] == 0:
                  clinic = Medical_Clinic.objects.filter(name=serializer.validated_data['name']).first()
                  if not clinic:
                      clinic = Medical_Clinic.objects.create(
                          name=serializer.validated_data['name'],
                          color=serializer.validated_data['color'],
                      )
                      clinic.save()
                      return Response({'response': 'Clinic created'}, status=status.HTTP_201_CREATED)
                  else:
                      return Response({'error': 'Clinic already exists'}, status=status.HTTP_409_CONFLICT)
              else:
                  return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
          else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
          return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ListClinicsView(APIView):
    @extend_schema(
        summary="List Clinics API",
        description="List all clinics."
                    "Token received in the Authorization header.",
        responses={
            200: {
                "description": "Successful request - Returns a success message.",
                "example": {
                    "response": [
                        {
                            "name": "Clinic 1",
                            "color": "#000000"
                        }
                    ]
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
                if validation['type'] == 0 or validation['type'] == 2:
                    clinics = Medical_Clinic.objects.filter(searchable=True)
                    serializer = ListClinicSerializer(clinics, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteClinicView(APIView):
    @extend_schema(
        summary="Delete Clinic API",
        description="Delete Clinic. Token received in the Authorization header.",
        request=ClinicSerializer,
        parameters=[
            OpenApiParameter(
                name="name",
                description="Clinic's name.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            )
        ],
        responses={
            200: {
                "description": "Delete Clinic - Returns a success message.",
                "example": {
                    "response": "Clinic deleted"
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
                "description": "Not Found. Clinic not found.",
                "example": {
                    "error": "Clinic not found"
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
    def delete(self, request):
        try:
            serializer = ClinicSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0:
                    clinic = Medical_Clinic.objects.get(name=serializer.validated_data['name'])
                    if clinic.searchable:
                        clinic.searchable = False
                        clinic.name = f'{clinic.name}-D{clinic.id}'
                        clinic.save()
                        return Response({'response': 'Clinic deleted'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except Medical_Clinic.DoesNotExist:
            return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FindClinicView(APIView):
    @extend_schema(
        summary="Find Clinic API",
        description="Find Clinic. Token received in the Authorization header.",
        request=ClinicSerializer,
        parameters=[
            OpenApiParameter(
                name="name",
                description="Clinic's name.",
                required=True,
                type=OpenApiTypes.STR,
                location="path",
            )
        ],
        responses={
            200: {
                "description": "Find Clinic - Returns a clinic.",
                "example": {
                    "name": "Clinic Name",
                    "color": "#000000"
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
                "description": "Not Found. Clinic not found.",
                "example": {
                    "error": "Clinic not found"
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
    def get(self, request,):
        try:
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0 or validation['type'] == 2:
                    name_serializer = ClinicSerializer(data = self.request.query_params)
                    name_serializer.is_valid(raise_exception=True)
                    clinic = Medical_Clinic.objects.get(name=name_serializer.validated_data['name'], searchable=True)
                    serializer = ListClinicSerializer(clinic)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Medical_Clinic.DoesNotExist:
            return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)