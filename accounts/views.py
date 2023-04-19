from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django_rest_passwordreset.views import (ResetPasswordRequestToken, ResetPasswordConfirm,
                                             ResetPasswordValidateToken)
from .models import User
from accounts.serializer import (UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
                                 UserChangePasswordSerializer)
from pizza.message import *
from rest_framework_simplejwt.tokens import AccessToken

# generating custom token

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    """
    This method is used for generating token. 
    """

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Create your views here.


class UserRegistration(APIView):
    """
    User Registration view.
    """

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({"token": token, "msg": "Registration Successful","data":serializer.data}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def user_detail(request):
    token = request.data['access']
    access_token = AccessToken(token)
    user = User.objects.filter(id=access_token['user_id'])
    serialized_data = UserProfileSerializer(instance=user, many=True)
    return Response({"user": serialized_data.data})


class UserLogin(APIView):
    """
    User login view.
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            if user := authenticate(email=email, password=password):
                token = get_tokens_for_user(user)
                return Response({'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': {'non_field_errors': ['Email or password is not valid']}},
                                status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(APIView):
    """
    View for change password
    """

    permission_classes = [IsAuthenticated]
    """
    IsAuthenticated class used for verifying that user is must for this specified operation
    """

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({password_changed}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(viewsets.ModelViewSet):
    """
    This is userprofile class in which we use Model View set. In this class we use different-different methods
    as per our requirement.
    """
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class ResetPasswordConfirmView(ResetPasswordConfirm):
    """
    Overriding of ResetPassword class to customize message part.

    ResetPassword class works in three steps(token passing, token validation, token confirmation)
    """

    def post(self, request, *args, **kwargs):
        super(ResetPasswordConfirmView, self).post(request, *args, **kwargs)
        return Response({password_reset_success})


class ResetPasswordValidateView(ResetPasswordValidateToken):
    """
    this is a customized part of ResetPasswordValidateToken class.
    """

    def post(self, request, *args, **kwargs):
        super(ResetPasswordValidateView, self).post(request, *args, **kwargs)
        return Response({token_validation_success})


class ResetPasswordTokenView(ResetPasswordRequestToken):
    """
    this is a customized part of ResetPasswordRequestToken class.
    """

    def post(self, request, *args, **kwargs):
        super(ResetPasswordTokenView, self).post(request, *args, **kwargs)
        return Response({token_passed_successfully})

class UserRetrieve(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    # def get(self):

