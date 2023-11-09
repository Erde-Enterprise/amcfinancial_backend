from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


from ..models import  Medical_Clinic
from ..serializers import  RegisterClinicSerializer, ListClinicSerializer
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
        responses=ListClinicSerializer,
    )
    def get(self, request):
        try:
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0:
                    clinics = Medical_Clinic.objects.all()
                    serializer = ListClinicSerializer(clinics, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)