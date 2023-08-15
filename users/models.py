from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

from django.contrib.auth import get_user_model

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
    
class UserType(models.TextChoices):
    EXPERT = 'expert', 'Expert'
    USER = 'user', 'User'


class MyUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.USER,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return f'{self.email}'

class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    picture = models.ImageField(upload_to='profile_pictures', blank=True)

    def __str__(self):
        return self.user.email