from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
class UserManager(BaseUserManager):
    
    def create_user(self,email,name,tc,password=None,password2=None):
        """
        Creates and saves a user with given email, name, tc and password.
        """
        
        if not email:
            raise ValueError("User must have an email address.")

        user=self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )
        
        user.set_password(password)
        user.save(using=self._db)

        return user
        
    
    def create_superuser(self,email,name,tc,password=None):
        
        """
        Creates and saves a superuser with given email, name,tc and password
        """
        
        user=self.create_user(
            email,
            password=password,
            name=name,
            tc=tc
        )        
        user.is_admin=True
        user.save(using=self._db)

        return user


class CreatedModified(models.Model):
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class User(AbstractBaseUser,CreatedModified):
    email=models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True
    )
    
    name=models.CharField(max_length=200)
    tc=models.BooleanField()
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)
    
    objects=UserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['name','tc']


    def __str__(self):
        return self.email

    
    def has_permissions(self,perm,obj=None):
        return self.is_admin

    
    def has_module_permissions(self,app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
        

class ForgotPassword(models.Model):
    
    otp=models.IntegerField(null=False)
    
    created_at=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
