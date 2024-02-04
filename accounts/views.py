from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.renderers import UserRenderer
from accounts.serializers import (EmailSerializer,
                                  SendPasswordResetEmailSerializer,
                                  UserChangePasswordSerializer,
                                  UserLoginSerializer, UserOTPSerializer,
                                  UserPasswordResetSerializer,
                                  UserProfileSerializer,
                                  UserRegistrationSerializer)


def get_tokens_for_user(user):
    refresh=RefreshToken.for_user(user)
    return {
        'refresh':str(refresh),
        'access':str(refresh.access_token)
    }
    

class UserRegistrationView(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        serializer=UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        token=get_tokens_for_user(user)
        
        return Response({'token':token,'msg':'Registration successful'},
                        status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    renderer_classes=[UserRenderer]
    
    def post(self,request,format=None):
        serializer=UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.data.get('email')
        password=serializer.data.get('password')

        user=authenticate(email=email,password=password)
        if user is None:
            return Response({'errors':{'non-field_errors':['Email or password is not valid']}},status=status.HTTP_404_NOT_FOUND)

        token=get_tokens_for_user(user)
        return Response({'token':token,'msg':'Login success'},status=status.HTTP_200_OK)


        
class UserProfileView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def get(self,request,format=None):
        serializer=UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self,request,format=None):
        serializer=UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        
        return Response({'msg':'Password changed successfully'},status=status.HTTP_200_OK)



class SendPasswordResetEmailView(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        serializer=SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password reset link sent. Please check your email'},status=status.HTTP_200_OK)
    

class UserPasswordResetView(APIView):
    renderer_classes=[UserRenderer]
    
    def post(self,request,uid,token,format=None):
        serializer=UserPasswordResetSerializer(data=request.data,context={'uid':uid,'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password reset successfully.'},status=status.HTTP_200_OK)
    

class VerifyOTP(APIView):
    
    permission_classes=[AllowAny]
    def post(self,request):
        email_serializer=EmailSerializer(data=request.data)
        if not email_serializer.is_valid(raise_exception=True):
            return Response(email_serializer.errors,status=status.HTTP_400_BAD_REQUEST)            

        otp_serializer=UserOTPSerializer(data=request.data)
        if not otp_serializer.is_valid(raise_exception=True):
            return Response(otp_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
        return Response(otp_serializer.data,status=status.HTTP_200_OK)