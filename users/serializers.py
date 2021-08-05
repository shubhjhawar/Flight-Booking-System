from rest_framework import serializers
from .models import UserRegistrationModel, UserRegistrationDetailModel, FlightModel,UserFlightModel, FlightImageModel


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRegistrationModel                   #using basic info model
        fields = '__all__'
    
    def validate(self, attrs):                          #checks if username and email exists already
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if UserRegistrationModel.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': "email already exists"})
        if UserRegistrationModel.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': "username already exists"})

        return super().validate(attrs)




class UserDetailSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserRegistrationDetailModel                       #using extra info model
        fields = ["gender","address1","address2","city","phone_number","state","country"]



class UserProfileSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserRegistrationModel                      #using basic info model
        fields = ["id","first_name", "last_name", "username", "email","role"]


class FlightSerializer(serializers.ModelSerializer):
    #this serializer is used to show data of a flight
    class Meta:
        model = FlightModel
        fields = ['id','company','arrival','departure','distance','price']


class UserFlightSerializer(serializers.ModelSerializer):
    # this serializer is used to show user_id and the id of the flights, the user has booked
    class Meta:
        model = UserFlightModel
        fields = ['user_info','flight_info']

class UserStatusSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserRegistrationModel                      #using basic info model
        fields = ["id","first_name", "last_name", "username", "email","is_active"]


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlightImageModel
        fields = ['flight_info', 'flight_image']
