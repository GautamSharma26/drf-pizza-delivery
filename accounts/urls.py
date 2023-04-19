from django.urls import path
from rest_framework_simplejwt.views import token_refresh, TokenBlacklistView, TokenObtainPairView
from .views import (UserRegistration, UserLogin, UserChangePasswordView, ResetPasswordConfirmView,
                    ResetPasswordValidateView, ResetPasswordTokenView, UserProfile, user_detail, UserRetrieve)


urlpatterns = [
    path("generate_access_token/", token_refresh),
    path('user_register/', UserRegistration.as_view(), name='register'),
    # path('login/', UserLogin.as_view(), name='login'),
    path('login/',TokenObtainPairView.as_view(),name="login"),
    path('logout/', TokenBlacklistView.as_view(),name="logout"),
    path('', UserProfile.as_view({'get': 'list'}), name='users'),
    path('change_password/', UserChangePasswordView.as_view(), name='change_password'),
    path('validate/', ResetPasswordValidateView.as_view()),
    path('password_reset/confirm/', ResetPasswordConfirmView.as_view(), name="password-reset-confirm"),
    path('password_reset/', ResetPasswordTokenView.as_view()),
    path('user-detail/',user_detail),
    path('user_detail/<int:pk>/', UserRetrieve.as_view())
    ]
