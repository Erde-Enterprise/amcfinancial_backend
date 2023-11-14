from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.core.exceptions import ValidationError
import base64


from ..models import Medical_Clinic, Invoice
from ..serializers import RegisterInvoiceSerializer, ListInvoicesSerializer, AttachmentSerializer, InvoiceSerializer, UpdateInvoiceSerializer
from ..middleware import teste_token
from ..provides import user_profile_type

class RegisterInvoiceView(APIView):
    @extend_schema(
        summary="Register Invoice API",
        description="Registers a new invoice."
                    "Token received in the Authorization header.",
        request=RegisterInvoiceSerializer,
        parameters=[
            OpenApiParameter(
                name="invoice_number",
                description="Invoice's number.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="description",
                description="Invoice's description.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="amount",
                description="Invoice's amount.",
                required=True,
                type=OpenApiTypes.INT,
                location="form",
            ),
            OpenApiParameter(
                name="title",
                description="Invoice's title.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="issue_date",
                description="Invoice's issue date.",
                required=True,
                type=OpenApiTypes.DATE,
                location="form",
            ),
            OpenApiParameter(
                name="due_date",
                description="Invoice's due date.",
                required=True,
                type=OpenApiTypes.DATE,
                location="form",
            ),
            OpenApiParameter(
                name="attachment",
                description="Invoice's attachment.",
                required=True,
                type=OpenApiTypes.BINARY,
            ),
            OpenApiParameter(
                name="reminder",
                description="Invoice's reminder (Mahnung).",
                required=False,
                type=OpenApiTypes.INT,  
            ),
            OpenApiParameter(
                name="status",
                description="Invoice's status.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="type",
                description="Invoice's type.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="name_clinic",
                description="Clinic's name.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            )
        ],
        responses={
            201: {
                "description": "Successful registration - Returns a success message.",
                "example": {
                    "response": "Invoice created"
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
            409: {
                "description": "Conflict. Invoice with this number already exists.",
                "example": {
                    "error": "Invoice already exists"
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
            serializer = RegisterInvoiceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0 or validation['type'] == 2:
                    attachment_bytes = request.FILES['attachment'].read() 
                    invoice = Invoice.objects.filter(invoice_number=serializer.validated_data['invoice_number']).first()
                    clinic = Medical_Clinic.objects.filter(name=serializer.validated_data['name_clinic']).first()
                    if clinic:
                      if not invoice:
                          user = user_profile_type(validation)
                          invoice = Invoice.objects.create(
                              invoice_number=serializer.validated_data['invoice_number'],
                              description=serializer.validated_data.get('description', ''),
                              amount=serializer.validated_data['amount'],
                              title=serializer.validated_data['title'],
                              issue_date=serializer.validated_data['issue_date'],
                              due_date=serializer.validated_data['due_date'],
                              attachment=attachment_bytes,
                              reminder= serializer.validated_data.get('reminder', 0),
                              status=serializer.validated_data['status'],
                              type=serializer.validated_data['type'],
                              clinic=clinic,
                              user= user
                          )
                          invoice.save()
                          return Response({'response': 'Invoice created'}, status=status.HTTP_201_CREATED)
                      else:
                          return Response({'error': 'Invoice already exists'}, status=status.HTTP_409_CONFLICT)
                    else:
                        return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
class DeleteInvoiceView(APIView):
    @extend_schema(
        summary="Delete Invoice API",
        description="Delete Invoice. Token received in the Authorization header.",
        parameters=[
            OpenApiParameter(
                name="invoice_number",
                description="Invoice's number.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            )
        ],
        responses={
            200: {
                "description": "Successful deletion - Returns a success message.",
                "example": {
                    "response": "Invoice deleted"
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
                "description": "Not Found. Invoice not found.",
                "example": {
                    "error": "Invoice not found"
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
            validation = teste_token(request.headers)
            serializer = InvoiceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if validation['validity']:
                if validation['type'] == 0:
                    invoice = Invoice.objects.filter(invoice_number=serializer.validated_data['invoice_number']).first()
                    if invoice:
                        invoice.delete()
                        return Response({'response': 'Invoice deleted'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
          errors = dict(e.detail)
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ListInvoicesView(APIView):
    @extend_schema(
        summary="List Invoices API",
        description="Returns all invoices if no parameters are passed. If 'Size' is passed, its value will be the number of Invoices returned."
                    "Token received in the Authorization header.",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Start date.",
                required=False,
                type=OpenApiTypes.STR,
                location="path",
            ),
            OpenApiParameter(
                name="end_date",
                description="End date.",
                required=False,
                type=OpenApiTypes.STR,
                location="path",
            )
        ],
        responses={
            200: {
                "description": "GET request successful. Returns a list of invoices.",
                "example": {
                    "clinic": {
                      "name": "Clinic Name",
                      "color": "Color"
                    },
                    "invoice_number": "Invoice Number",
                    "description": "Description of the invoice",
                    "amount": "100",
                    "title": "Title",
                    "issue_date": "2023-05-01",
                    "due_date": "2023-05-01",
                    "reminder": 0,
                    "status": "Pending",
                    "type": "Invoice",

                }
            },
            400: {
                "description": "Bad request. Missing/invalid parameters.",
                "example": {
                    "error": "Bad request. Missing/invalid parameters."
                }
            },
            401: {
                "description": "Invalid token or Activation Expired.",
                "example": {
                    "error": "Invalid token or Activation Expired."
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
            start_date = self.request.query_params.get('start_date', None)
            end_date = self.request.query_params.get('end_date', None)
            if start_date and end_date:
              invoices = Invoice.objects.filter(issue_date__range=[start_date, end_date])
            elif start_date:
              invoices = Invoice.objects.filter(issue_date__gte=start_date)
            elif end_date:
              invoices = Invoice.objects.filter(issue_date__lte=end_date)
            else:
              invoices = Invoice.objects.all()
            reponse_serializer = ListInvoicesSerializer(invoices, many=True)
            return Response(reponse_serializer.data, status=status.HTTP_200_OK)
          else:
            return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            errors = {'error': str(e)}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AttachmentView(APIView):
    @extend_schema(
        summary="Get Attachment API",
        description="Gets the attachment of an invoice."
                    "Token received in the Authorization header.",
        request=AttachmentSerializer,
        parameters=[
            OpenApiParameter(
                name="invoice_number",
                description="Invoice's number.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            )
        ],
        responses=
        {
            200: {
                "description": "GET request successful. Returns the attachment of the invoice.",
                "example": {
                    "attachment": "base64 encoded string"
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
                    "error": "Invalid token or Activation Expired."
                }
            },
            404: {
                "description": "Invoice not found.",
                "example": {
                    "error": "Invoice not found"
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
          validation = teste_token(request.headers)
          serializer = AttachmentSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          if validation['validity']:
              invoice = Invoice.objects.get(invoice_number=serializer.validated_data['invoice_number'])
              attachment_data = invoice.attachment
              attachment_base64 = base64.b64encode(attachment_data).decode('utf-8') 
              return Response({'attachment': attachment_base64}, status=status.HTTP_200_OK)
          else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateInvoiceView(APIView):
    @extend_schema(
        summary="Update Invoice API",
        description="Updates an invoice."
                    "Token received in the Authorization header.",
        request=UpdateInvoiceSerializer,
        parameters=[
            OpenApiParameter(
                name="invoice_number_older",
                description="Invoice's number older.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="invoice_number",
                description="Invoice's number.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",

            ),
            OpenApiParameter(
                name="description",
                description="Description of the invoice.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="amount",
                description="Amount of the invoice.",
                required=False,
                type=OpenApiTypes.INT,
                location="form",
            ),
            OpenApiParameter(
                name="title",
                description="Title of the invoice.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="issue_date",
                description="Issue Date of the invoice.",
                required=False,
                type=OpenApiTypes.DATE,
                location="form",
            ),
            OpenApiParameter(
                name="due_date",
                description="Due Date of the invoice.",
                required=False,
                type=OpenApiTypes.DATE,
                location="form",
            ),
            OpenApiParameter(
                name="attachment",
                description="Attachment of the invoice.",
                required=False,
                type=OpenApiTypes.BINARY,
                location="form",
            ),
            OpenApiParameter(
                name="reminder",
                description="Reminder of the invoice.",
                required=False,
                type=OpenApiTypes.INT,
                location="form",
            ),
            OpenApiParameter(
                name="status",
                description="Status of the invoice.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="type",
                description="Type of the invoice.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="name_clinic",
                description="Name of the clinic.",
                required=False,
                type=OpenApiTypes.STR,
                location="form",
            )
        ],
        responses={
            200: {
                "description": "Invoice updated.",
                "example": {
                    "response": "Invoice updated"
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
                "description": "Invoice not found.",
                "example": {
                    "error": "Invoice not found"
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
    def patch(self, request):
        try:
           data_copy = request.data.copy()
           invoice_number_older = data_copy.pop('invoice_number_older', None)
           invoice = Invoice.objects.get(invoice_number=invoice_number_older)
           validation = teste_token(request.headers)
           if validation['validity']:
              if validation['type'] == 0  or validation['type'] == 2:
                 name_clinic = data_copy.pop('name_clinic', None)
                 if name_clinic:
                    clinic = Medical_Clinic.objects.get(name=name_clinic)
                    if clinic:
                       invoice.clinic = clinic
                    else:
                       return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
                 attachment = data_copy.pop('attachment', None)
                 if attachment:
                    attachment_bytes = request.FILES['attachment'].read() 
                    invoice.attachment = attachment_bytes
                 serializer = UpdateInvoiceSerializer(invoice, data=data_copy, partial=True)
                 serializer.is_valid(raise_exception=True)
                 serializer.save()
                 return Response({'response': 'Invoice updated'}, status=status.HTTP_200_OK)
              else:
                 return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
           else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
          errors = dict(e.detail)  
          return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        