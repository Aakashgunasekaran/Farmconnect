from django.db import models
from django.conf import settings  
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.models import User

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, default='Unknown')
    kisan_id = models.CharField(max_length=20, unique=True)
    dob = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'kisan_id', 'dob']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Product(models.Model):
    product_id = models.CharField(max_length=5, primary_key=True)
    farmer_id = models.CharField(max_length=5, null=True)
    product_name = models.CharField(max_length=15, null=True)
    category = models.CharField(max_length=20, null=True)
    description = models.CharField(max_length=75, null=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    harvest_date = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    organic = models.CharField(max_length=10, default='no', null=True)

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        if self.farmer_id:
            self.farmer_id = self.farmer_id.strip()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'product'

from django.db import models
from django.contrib.auth.models import User

class CropRecommendation(models.Model):
    state_name = models.CharField(max_length=255)
    district_name = models.CharField(max_length=255)
    crop_year = models.IntegerField()
    season = models.CharField(max_length=255)
    crop = models.CharField(max_length=255, default='Unknown Crop') 
    recommended_crop = models.CharField(max_length=255)  # Assuming you have a recommended crop field
    area = models.FloatField()
    production = models.FloatField()

    def __str__(self):
        return f"{self.recommended_crop} for {self.state_name} ({self.crop_year})"

def predict_crop(temp, humidity, rainfall, soil_type):
    # Example logic: you can replace this with an actual ML model
    if temp > 30 and rainfall > 100:
        return "Paddy"
    elif humidity < 50:
        return "Wheat"
    elif soil_type == "loamy":
        return "Maize"
    else:
        return "Millet"
    

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
