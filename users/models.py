from django.db import models
from phone_field import PhoneField
import string
import random
# Create your models here.


status = (
    ('0', 'inactive'),
    ('1', 'active'),
)
ROLES = (
    ('0', 'user'),
    ('1', 'admin'),
)

def generate_activation_code():                         #this function is used to generate a 6 letter code which is unique to all the new users
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))


class UserRegistrationModel(models.Model):                                           #model for user's basic information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=25)
    email = models.EmailField()
    password = models.CharField(max_length=500)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    is_active = models.CharField(max_length=20, choices=status, default='inactive')
    code = models.CharField(max_length=6, default=generate_activation_code)

class UserRegistrationDetailModel(models.Model):                                     #model for storing user's extra information
    user_info = models.ForeignKey(UserRegistrationModel, on_delete=models.CASCADE)   #foreign key used to connect the two models
    gender = models.CharField(max_length=10)
    phone_number = PhoneField()
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    date_joined = models.DateTimeField(default=None)
    modified_date = models.DateTimeField(default=None)

class FlightModel(models.Model):
    company = models.CharField(max_length=30)
    distance = models.IntegerField()
    arrival = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    price = models.IntegerField()
    is_active = models.CharField(max_length=20, choices=status, default='active')


class UserFlightModel(models.Model):
    user_info = models.ForeignKey(UserRegistrationModel, on_delete=models.CASCADE)
    flight_info = models.ForeignKey(FlightModel, on_delete=models.CASCADE)
    date_of_booking = models.DateField(default=None)


class FlightImageModel(models.Model):
    flight_info = models.ForeignKey(FlightModel, on_delete=models.CASCADE)
    flight_image = models.ImageField(null=True, blank=True, upload_to='images/')