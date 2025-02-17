import jwt
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager, UserManager
from django.db import models
from datetime import datetime, timedelta

from atmacacode import settings


# Create your models here.

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError("Password is not provided")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_activated', True)
        return self._create_user(email, password, first_name, last_name, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, max_length=255, verbose_name="E-Posta")
    username = models.CharField(max_length=100, unique=False, blank=True, null=True, default=None)
    first_name = models.CharField(max_length=255, verbose_name="Ad")
    last_name = models.CharField(max_length=255, verbose_name="Soyad")
    mobile = models.CharField(max_length=50, verbose_name="Telefon Numarası", blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    is_staff = models.BooleanField(default=True, verbose_name="Personel")
    is_customer = models.BooleanField(default=False, verbose_name="Müşteri")
    is_student = models.BooleanField(default=False, verbose_name="Öğrenci")
    is_superuser = models.BooleanField(default=False, verbose_name="Admin")
    is_activated = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def token(self):
        token = jwt.encode({'username': self.username, 'email': self.email, 'exp': datetime.utcnow()+timedelta(hours=24)},settings.SECRET_KEY, algorithm='HS256')
        return token

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"
    
    @property
    def get_permission(self):
        return self.u_permission.filter(user=self)