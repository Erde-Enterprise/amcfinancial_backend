from django.urls import path
from .views.customer import RegisterCustomerView, DeleteCustomerView
from .views.others import ValidateTokenView, LoginView
from .views.invoice import RegisterInvoiceView, ListInvoicesView, AttachmentView, DeleteInvoiceView
from .views.clinic import RegisterClinicView    
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('validate-token/',ValidateTokenView.as_view(), name='validate-token'),
    # REGISTER
    path('register/customer/', RegisterCustomerView.as_view(), name='register-customer'), 
    path('register/clinic/', RegisterClinicView.as_view(), name='register-clinic'),
    path('register/invoice/', RegisterInvoiceView.as_view(), name='register-invoice'),
    # LIST
    path('list/invoices/', ListInvoicesView.as_view(), name='list-all-invoices'),
    # DELETE
    path('delete/customer/', DeleteCustomerView.as_view(), name='delete-customer'),
    path('delete/invoice/', DeleteInvoiceView.as_view(), name='delete-invoice'),
    # OTHERS
    path('attachment/', AttachmentView.as_view(), name='attachment'),
    # SWAGGER
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

