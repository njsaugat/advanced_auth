from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from rest_framework import serializers
# from rest_framework.validators import MinValueValidator

from decouple import config
from accounts.models import User,ForgotPassword
from accounts.utils import Util
from datetime import timedelta,datetime
class UserRegistrationSerializer(serializers.ModelSerializer):
    password=serializers.CharField(style={'input_type':'password'},write_only=True)
    
    class Meta:
        model=User
        fields=['email','name','password','password2','tc']    
        extra_kwargs={
            'password':{'write_only':True}
        }
        
        
    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')

        if password!=password2:
            raise serializers.ValidationError("Both the passwords must match.")
        
        return attrs
    
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
    

class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)

    class Meta:
        model=User
        fields=['email','password']


class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=['id','email','name']
    
    

class UserChangePasswordSerializer(serializers.Serializer):
    
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields=['password','password2']
    
    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        user=self.context.get('user')
        if password!=password2:
            raise serializers.ValidationError("Both the passwords must match")
        
        user.set_password(password)
        user.save()
        return attrs
    
    
class EmailSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)   

    class Meta:
        fields=['email']
      
    def validate(self, attrs):
        email=attrs.get('email')

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("The email isn't registered.")
        
        return attrs  

class SendPasswordResetEmailSerializer(EmailSerializer):

    
    def validate(self,attrs):
        super().validate(attrs)
        email=attrs.get('email')

        user=User.objects.get(email=email)
        generated_otp=Util.generate_otp()
        
        new_otp=ForgotPassword.objects.create(otp=generated_otp,user=user)
        new_otp.save()

        uid=Util.generate_uid()[:8]
        token=PasswordResetTokenGenerator().make_token(user)

        link=config("BASE_URL")+ reverse('reset-password', args=[uid, token])

        body=f"""Click following link to reset your password. 
        
        {link}  
        
        The generated otp is <b> {str(generated_otp)} </b> """

        data={
            'subject':'Reset your password',
            'body':body,
            'to_email':user.email
        }
        Util.send_email(data)
        return attrs
    
class UserPasswordResetSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields=['password','password2']
    
    
    def validate(self,attrs):
        try:
            password=attrs.get('password')
            password2=attrs.get('password2')
            uid=self.context.get('uid')
            token=self.context.get('token')

            if password!=password2:
                raise serializers.ValidationError("Both passwords don't match.")
            
            id=smart_str(urlsafe_base64_decode(uid))
            user=User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                raise serializers.ValidationError('Token is not valid or expired')
            
            user.set_password(password)        
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise serializers.ValidationError('Token is not valid or expired.')
        
        
        
class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        fields='__all__'

    
class UserOTPSerializer(serializers.Serializer):
    
    otp=serializers.IntegerField()
    
    def validate(self, validated_data):
        otp=validated_data.get('otp')
        existing_otp=ForgotPassword.objects.filter(otp=otp).first()

        if (not existing_otp or otp!=existing_otp.otp):
            raise serializers.ValidationError("The otp you entered is invalid.")

        timeout_duration=getattr(settings,'PASSWORD_RESET_TIMEOUT',900)

        if existing_otp.created_at + timedelta(seconds=timeout_duration) < timezone.now():
            raise serializers.ValidationError("The otp is already expired.")
        
        return validated_data