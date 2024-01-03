from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Case, When, Value, IntegerField
from django.db import IntegrityError
import base64

from ..models import Medical_Clinic, Invoice
from ..serializers import RegisterInvoiceSerializer, ListInvoicesSerializer, AttachmentSerializer, InvoiceSerializer, UpdateInvoiceSerializer
from ..middleware import teste_token
from ..provides import user_profile_type, get_file_mime_type

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
                type=OpenApiTypes.STR,
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
                name="scheduled_date",
                description="Invoice's scheduled date.",
                required=False,
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
                          reminder = serializer.validated_data.get('reminder', 0)
                          if reminder > 3:
                              reminder = 3
                          invoice = Invoice.objects.create(
                              invoice_number=serializer.validated_data['invoice_number'],
                              description=serializer.validated_data.get('description', ''),
                              amount=serializer.validated_data['amount'],
                              title=serializer.validated_data['title'],
                              issue_date=serializer.validated_data['issue_date'],
                              due_date=serializer.validated_data['due_date'],
                              scheduled_date=serializer.validated_data.get('scheduled_date', None),
                              attachment=attachment_bytes,
                              reminder=reminder,
                              status=serializer.validated_data['status'],
                              type=serializer.validated_data['type'],
                              clinic=clinic,
                              user=user
                          )
                          invoice.save()
                          return Response({'response': 'Invoice created'}, status=status.HTTP_201_CREATED)
                      else:
                          if invoice.searchable:
                            return Response({'error': 'Invoice already exists'}, status=status.HTTP_409_CONFLICT)
                          else:
                            return Response({'error': 'Number Invoice Invalid'}, status=status.HTTP_409_CONFLICT)
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
        request=InvoiceSerializer,
        parameters=[
            OpenApiParameter(
                name="invoices_number",
                description=" List of Invoice's number.",
                required=True,
                location="form",
                ),
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
                    invoices = Invoice.objects.filter(invoice_number__in=serializer.validated_data['invoices_number'], searchable=True)
                    if invoices.exists():
                        for invoice in invoices:
                            invoice.searchable = False
                            invoice.save()
                        return Response({'response': 'Invoice deleted'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
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

class FindInvoiceView(APIView):
   @extend_schema(
       summary="Find Invoice API",
       description="Find Invoice. Token received in the Authorization header.",
       parameters=[
           OpenApiParameter(
               name="invoice_number",
               description="Invoice's number.",
               required=True,
               type=str,
               location="path",
           )
       ],
       responses={
           200: {
               "description": "Successful search - Returns the Invoice.",
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
   def get(self, request):
        try:
            validation = teste_token(request.headers)
            if validation['validity']:
                if validation['type'] == 0 or validation['type'] == 2:
                    number_invoice = self.request.query_params.get('invoice_number', None)
                    invoice = Invoice.objects.get(invoice_number=number_invoice, searchable=True)
                    serializer = ListInvoicesSerializer(invoice)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ListInvoicesView(APIView):
    @extend_schema(
        summary="List Invoices API",
        description="Returns all invoices if no parameters are passed."
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
            date_filters = Q()
            if start_date and end_date:
              date_filters &= Q(due_date__range=[start_date, end_date])
            elif start_date:
              date_filters &= Q(due_date__gte=start_date)
            elif end_date:
              date_filters &= Q(due_date__lte=end_date)
            else:
              invoices = Invoice.objects.filter(searchable=True)
              invoices = self.annotate_status_priority(invoices)
              reponse_serializer = ListInvoicesSerializer(invoices, many=True)
              return Response(reponse_serializer.data, status=status.HTTP_200_OK)
            
            invoices = Invoice.objects.filter(date_filters | (~Q(reminder=0) & ~Q(status='P')), searchable=True)
            invoices = self.annotate_status_priority(invoices)
            reponse_serializer = ListInvoicesSerializer(invoices, many=True)
            return Response(reponse_serializer.data, status=status.HTTP_200_OK)
          else:
            return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
          
        except ValidationError as e:
            errors = {'error': str(e)}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            errors = {'error': str(e)}
            return Response(errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def annotate_status_priority(self, invoices):
        return invoices.annotate(
            status_priority=Case(
                When(Q(status='E'), then=Value(3)),
                When(Q(status='D'), then=Value(2)),
                When(Q(status='S'), then=Value(1)),
                When(Q(status='P'), then=Value(0)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-status_priority', '-reminder', 'due_date')

class AttachmentView(APIView):
    @extend_schema(
        summary="Get Attachment API",
        description="Gets the attachment of an invoice."
                    "Token received in the Authorization header. (The mime_type could be a aplication/* or image/*).",
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
                "description": "GET request successful. Returns the attachment of the invoice. (The mime_type could be a aplication/* or image/*).",
                "example": {
                    "attachment": "base64 encoded string",
                    "mime_type": "image/png" 
                },
                
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
              if invoice.searchable:
                attachment_data = invoice.attachment
                attachment_base64 = base64.b64encode(attachment_data).decode('utf-8') 
                mime_type = get_file_mime_type(attachment_data)
                return Response({'attachment': attachment_base64, 'mime_type': mime_type}, status=status.HTTP_200_OK)
              else:
                return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
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
                name="invoice_number",
                description="Invoice's number older.",
                required=True,
                type=OpenApiTypes.STR,
                location="form",
            ),
            OpenApiParameter(
                name="new_invoice_number",
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
                name="scheduled_date",
                description="Scheduled Date of the invoice.",
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
           validation = teste_token(request.headers)
           if validation['validity']:
              if validation['type'] == 0  or validation['type'] == 2: 
                 invoice_number = request.data['invoice_number']
                 invoice = Invoice.objects.get(invoice_number=invoice_number)
                 if invoice.searchable:
                    serializer = UpdateInvoiceSerializer(invoice, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'response': 'Invoice updated'}, status=status.HTTP_200_OK)
                 else:
                    return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
              else:
                 return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
           else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            error_message = e.detail[0] if isinstance(e.detail, list) else e.detail
            errors = {'error': error_message}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'error': 'Number Invoice already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SumAmountView(APIView):
   @extend_schema(
       summary="Sum of amount invoices.",
       description="Sum of all invoices not paid or scheduled.",
       parameters=[
           OpenApiParameter(
               name="scheduled_date",
               description="Scheduled Date of the invoice.",
               required=False,
               type=OpenApiTypes.DATE,
               location="path",
           )
       ],
       responses={
           200: {
               "description": "Sum of amount invoices.",
               "example": {
                   "sum": 152.38
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
              if validation['type'] == 0  or validation['type'] == 2: 
                 scheduled_date = self.request.query_params.get('scheduled_date', None)
                 if scheduled_date:
                    invoices = Invoice.objects.filter(scheduled_date=scheduled_date, searchable=True)
                    amount = 0
                    for invoice in invoices:
                       amount += invoice.amount
                    return Response({'response': amount}, status=status.HTTP_200_OK)
                 invoices = Invoice.objects.filter(~Q(status='P'), searchable=True)
                 amount = 0
                 for invoice in invoices:
                    amount += invoice.amount
                 return Response({'response': amount}, status=status.HTTP_200_OK)
              else:
                 return Response({'error': 'Invalid User Type'}, status=status.HTTP_403_FORBIDDEN)
           else:
              return Response({'error': 'Invalid token or Activation Expired'}, status=status.HTTP_401_UNAUTHORIZED)
       except:
           return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)