from django.urls import path
from .views import ValidateTokenView, LoginView, RegisterCustomerView, RegisterClinicView, RegisterInvoiceView, ListLatestInvoicesView, ListAllInvoicesView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('validate-token/',ValidateTokenView.as_view(), name='validate-token'),
    # REGISTER
    path('register/customer/', RegisterCustomerView.as_view(), name='register-customer'), 
    path('register/clinic/', RegisterClinicView.as_view(), name='register-clinic'),
    path('register/invoice/', RegisterInvoiceView.as_view(), name='register-invoice'),
    #LIST
    path('list/latest-invoices/', ListLatestInvoicesView.as_view(), name='list-latest-invoices'),
    path('list/all-invoices/', ListAllInvoicesView.as_view(), name='list-all-invoices'),
    # SWAGGER
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

