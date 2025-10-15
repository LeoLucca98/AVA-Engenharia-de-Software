from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import jwks

app_name = 'users'

urlpatterns = [
    # Endpoints de autenticação
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints de usuário
    path('user/', views.user_info, name='user_info'),
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Endpoints alternativos com classes
    path('auth/register/', views.UserRegistrationView.as_view(), name='auth_register'),
    path('auth/login/', views.UserLoginView.as_view(), name='auth_login'),
    
    # JWKS endpoint for JWT validation
    path('.well-known/jwks.json', jwks.jwks_endpoint, name='jwks'),
]
