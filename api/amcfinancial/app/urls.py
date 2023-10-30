from django.urls import path
from .views import ValidateTokenView, LoginView, RegisterCustomerView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.conf import settings
from django.conf.urls.static import static

validate_token_view = ValidateTokenView.as_view()
login_view = LoginView.as_view()
register_customer_view = RegisterCustomerView.as_view()

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('validate-token/',ValidateTokenView.as_view(), name='validate-token'),
    path('register-customer/', RegisterCustomerView.as_view(), name='register-customer'), 
    # SWAGGER
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
