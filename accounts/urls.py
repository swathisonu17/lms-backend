from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, UserDetailView
from .views import VerifyEmail
from .views import CustomTokenObtainPairView
from .views import ForgotPasswordView
from .views import ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),      # POST: /api/accounts/register/
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify/<uidb64>/<token>/', VerifyEmail.as_view(), name='verify-email'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
