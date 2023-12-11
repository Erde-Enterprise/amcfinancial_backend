from django.urls import path
from .views.others import LoginView
from .views.customer import RegisterCustomerView, DeleteCustomerView, ListCustomerView, UpdateCustomerView, FindCustomerView
from .views.invoice import RegisterInvoiceView, ListInvoicesView, AttachmentView, DeleteInvoiceView, UpdateInvoiceView, FindInvoiceView
from .views.clinic import RegisterClinicView, ListClinicsView, DeleteClinicView, FindClinicView, UpdateClinicView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # REGISTER
    path('register/customer/', RegisterCustomerView.as_view(), name='register-customer'), 
    path('register/clinic/', RegisterClinicView.as_view(), name='register-clinic'),
    path('register/invoice/', RegisterInvoiceView.as_view(), name='register-invoice'),

    # LIST
    path('list/invoices/', ListInvoicesView.as_view(), name='list-all-invoices'),
    path('list/clinics/', ListClinicsView.as_view(), name='list-all-clinics'),
    path('list/customers/', ListCustomerView.as_view(), name='list-all-customers'),

    # FIND
    path('find/invoice/', FindInvoiceView.as_view(), name='find-invoice'),
    path('find/customer/', FindCustomerView.as_view(), name='find-customer'),
    path('find/clinic/', FindClinicView.as_view(), name='find-clinic'),

    # DELETE
    path('delete/customer/', DeleteCustomerView.as_view(), name='delete-customer'),
    path('delete/invoice/', DeleteInvoiceView.as_view(), name='delete-invoice'),
    path('delete/clinic/', DeleteClinicView.as_view(), name='delete-clinic'),

    # UPDATE
    path('update/invoice/', UpdateInvoiceView.as_view(), name='update-invoice'),
    path('update/customer/', UpdateCustomerView.as_view(), name='update-customer'),
    path('update/clinic/', UpdateClinicView.as_view(), name='update-clinic'),

    # OTHERS
    path('attachment/', AttachmentView.as_view(), name='attachment'),
    path('login/', LoginView.as_view(), name='login'),
    
    # SWAGGER
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

