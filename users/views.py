from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from .serializers import UserRegistrationSerializer,UserDetailSerializer,UserProfileSerializer,FlightSerializer, UserFlightSerializer, UserStatusSerializer, ImageSerializer
from rest_framework.response import Response
from rest_framework import status, viewsets
from datetime import datetime, date, timedelta
from .models import UserRegistrationModel, UserRegistrationDetailModel, FlightModel, UserFlightModel, FlightImageModel
from rest_framework.decorators import action
from .utils import *
from .messages import *
from django.contrib.auth.hashers import make_password, check_password
import logging
logger = logging.getLogger('django')

# Create your views here.


class RegisterView(GenericAPIView):
    #used to register a new user into the system
    serializer_class = UserRegistrationSerializer

    def post(self,request):                                 #register a new user
        serializer = UserRegistrationSerializer(data=request.data)
        header = request.headers                            # storing all the information from the headers here
        is_admin = int(header['admin'])
        password = request.data.get('password', '')            #first we get the password from the request parameter
        encrypted_password =make_password(password)             #then we encrypt the password
        if serializer.is_valid():                           #if data is valid
            if is_admin == 1:
                serializer.save(role='admin', password = encrypted_password)                               #data is stored in the database along with the encrypted password
            else:
                serializer.save(role='user', password = encrypted_password)

            user_id = serializer.data['id']
            user_info = UserRegistrationModel(id=user_id)      #foreign key used to connect the two models
            request.data["date_joined"] = datetime.now()
            request.data["modified_date"] = datetime.now()
            request.data["user_info_id"] = user_info
            user_detail_serializer = UserDetailSerializer(data=request.data)
            user_detail_serializer.is_valid()
            user_detail_serializer.save(user_info=user_info,date_joined=datetime.now(),modified_date=datetime.now())

            password = request.data.get('password', '')
            domain = get_current_site(request).domain           #get the domain of the application
            code = serializer.data['code']                      #used to get the 6letter code generated earlier
            link = reverse('activate',kwargs={'code':code})     #this is used to extract information from the URL named as 'activate'
            activate_url = 'http://'+domain+link                #this is the URL created which is then passed in the email as is used as an API to activate the said user

            username = serializer.data['username']
            
            data = "You have registered successfully. Your username is "+username+", your password is "+password+".\n" + "Please click on this link to activate your account-\n"+activate_url

            send_mail('Registration - Flight Booking System',
                      data,
                      'jhawar556shubh@gmail.com',
                      [serializer.data['email']]
                      )

            logger.info('user registered successfully')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.info('user did not get registered')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccount(GenericAPIView):
    #this API is used to activate a new user via email
    def get(self,request,code):
        try:
            user = UserRegistrationModel.objects.get(code=code)             #we pass code in the URL and then fetch the user object having that code
            user.is_active = 'active'
            user.save(update_fields=['is_active'])                          #then status of that user is changed to active
            return Response({"success": activation_success_msg},status=status.HTTP_200_OK)
        except Exception:
            return Response({"failure": failure_msg},status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    #used to login a user
    def post(self, request):                                                        # login a user
        data = request.data
        username = data.get('username', '')                                         # getting user/admin username and password
        password = data.get('password', '')
        header = request.headers                                                    # storing all the information from the headers here
        is_admin = int(header['admin'])                                             # is_admin is use to differentiate between an admin an user by 'admin = 1' in header
        try:
            user_info = UserRegistrationModel.objects.get(username=username)   #model object having the corressponding username and password
            encrypted_password = user_info.password
            correct_password =check_password(password,encrypted_password)
            if correct_password==True:
                if is_admin == 1 and user_info.role == 'admin':                                     #if is_admin is 1 and role in that model object is admin
                    serializer = UserProfileSerializer
                    admin = serializer(user_info)
                    user_id = admin.data['id']
                    username = admin.data['username']
                    role = admin.data['role']
                    now = datetime.now()
                    now_30 = str(now + timedelta(minutes=30))
                    payload={
                        "user_id":user_id,
                        "username":username,
                        "role":role,
                        "valid_time": now_30
                    }
                    encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
                    logger.info('admin is logged in successfully')
                    return Response(({"success": login_success_msg, 'token':encoded_jwt},), status=status.HTTP_200_OK)       #admin is logged in
                elif is_admin == 0 and user_info.role == 'user':                                                                               #when role is user and even if is_admin=1, user is logged in
                    serializer = UserProfileSerializer
                    user = serializer(user_info)
                    user_id = user.data['id']
                    username = user.data['username']
                    role = user.data['role']
                    now = datetime.now()
                    now_30 = str(now + timedelta(minutes=30))
                    payload = {
                        "user_id": user_id,
                        "username": username,
                        "role":role,
                        "valid_time": now_30
                    }
                    encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
                    logger.info('user is logged in successfully')
                    return Response(({"success": login_success_msg,'token':encoded_jwt}), status=status.HTTP_200_OK)
                else:
                    return Response({"failure": failure_msg}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"failure": failure_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info('error occurred while logging in')
            return Response({"failure": failure_msg}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(GenericAPIView):
    #this viewset shows us the information(profile) of a user
    def post(self, request):                            #this shows user profile
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                data = request.data
                id = data.get('id', '')
                user_info = UserRegistrationModel.objects.get(id=id)  # database object from the first modeel
                profile_serializer = UserProfileSerializer  # serializer for display of user information except
                basic_info = profile_serializer(user_info)
                user_id = user_info.id
                other_info = UserRegistrationDetailModel.objects.get(user_info=user_id)  # database object from the second model matched by the user_id provided by the first model
                extra_detail_serializer = UserDetailSerializer  # serializer for showing the extra details of the user
                extra_info = UserDetailSerializer(other_info)
                details = {}  # creating an empty usertionary and storing necessary data in it to show the user.
                details["id"] = user_info.id
                details["first_name"] = user_info.first_name
                details["last_name"] = user_info.last_name
                details["username"] = user_info.username
                details["first_name"] = user_info.first_name
                details["email"] = user_info.email
                details["phone_number"] = extra_info.data['phone_number']
                details["address1"] = extra_info.data['address1']
                details["address2"] = extra_info.data['address2']
                details["city"] = extra_info.data['city']
                details["state"] = extra_info.data['state']
                details["country"] = extra_info.data['country']

                if user_info:
                    logger.info('user details are shown successfully')
                    return Response({"resData": details}, status=status.HTTP_200_OK)
            else:
                return Response({"failure": invalid_token_msg},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info("error occurred while displaying the user's details")
            return Response({"failure": failure_msg}, status=status.HTTP_400_BAD_REQUEST)





class UserProfileUpdateView(GenericAPIView):
    #this is used to update the profile of a user
    def put(self,request):                          #function to update user's details
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                data = request.data
                update_basic_details(data)
                update_extra_details(data)
                logger.info("user's information is updated successfully")
                return Response({"success": profile_update_success_msg},status=status.HTTP_200_OK)
            else:
                return Response({"failure": invalid_token_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while updating user's information")
            return Response({"failure": exception_msg},status=status.HTTP_400_BAD_REQUEST)



class ChangePasswordView(GenericAPIView):
    #used to change the password a user

    def post(self,request):
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                data= request.data
                user_id = data.get('user_id','')
                old_password = data.get("old_password",'')          #getting the old and new password from the user
                new_password = data.get("new_password",'')

                user_object = UserRegistrationModel.objects.get(id=user_id)     #getting the model object of that user
                current_password = user_object.password                         #storing the password in use in current_password
                if current_password == old_password:                            #if old password provided by the user matche the real password
                    user_object.password = new_password                         #then only password is updated to new_password
                    user_object.save(update_fields=['password'])
                    logger.info('Password successfully updated')
                    return Response({"success": password_update_success_msg},status=status.HTTP_200_OK)
                logger.info('old password doesnt match')
                return Response({"Failure": password_update_failure_msg},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while updating user's password")
            return Response({"failure": exception_msg},status=status.HTTP_400_BAD_REQUEST)




class FlightView(GenericAPIView):
    #this APTView is for viewing flights in the system and viewing them all
    def get(self, request):                         #here we can see all the flights that our system is offering
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                serializer = FlightSerializer
                queryset = FlightModel.objects.filter(is_active = 'active')
                all_flights = serializer(queryset,many=True)
                logger.info("all the available flights are displayed successfully")
                return Response(all_flights.data, status=status.HTTP_200_OK)
            else:
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while displaying all the flights")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)


class BookFlightView(GenericAPIView):
    #this APIBiew belongs to booking flights
    def post(self,request):                                 #by post request we ask user to put a flight
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                serializer = UserFlightSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(date_of_booking=date.today())
                    logger.info("flight was booked successfully")
                    return Response({"success": flight_booked_success_msg}, status=status.HTTP_201_CREATED)
            else:
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while booking a flight")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)

    # get request takes pk(primary key) in url as user id and it shows all the flights booked by that user
    def get(self,request,user_id):
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                booked_flights_info = UserFlightModel.objects.filter(user_info = user_id)      #filtering all the flight_ids regarding this particular user
                if booked_flights_info:                                                         #this checks if the user has booked any flight or not
                    booked_flights = []                                                     #empty list which will save all the flights
                    for i in booked_flights_info:                                                     #for all the flights in flight_ids
                        booked_flight = i.flight_info                        #flight object is recieveed with the help of the flight_info
                        flight_serializer = FlightSerializer
                        booked_flight = flight_serializer(booked_flight)        #object model is passed into it's corresponding serializer
                        booked_flights.append(booked_flight.data)                  #after passing throght the serializer data of that flight is stored in the list
                    logger.info("all the flights booked by a user is displayed successfully")
                    return Response(booked_flights, status=status.HTTP_200_OK)
                else:
                    logger.info("asking user to book a flight first")
                    return Response({"failure": book_flights_msg}, status=status.HTTP_204_NO_CONTENT)          #message returned if no flights are booked
            else:
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while displaying flights booked by a user")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(GenericAPIView):
    #this API is used to display all the users
    def get(self,request):
        try:
            token = request.headers['Authorization']
            if check_admin_token(token)==True:                                                 #if an admin is using this
                user_list = []                                                  # declaring an empty list
                user_objects = UserRegistrationModel.objects.all()              # get all the user model objects
                user_serializer = UserProfileSerializer                         # initiating two serializers
                details_serializer = UserDetailSerializer
                for user_object in user_objects:                                #iterating through all the users
                    user_object = user_serializer(user_object)                  #pass the objects models through a aserializer
                    extra_info_object = UserRegistrationDetailModel.objects.get(id = user_object.data['id'])    # getting the extra detail model corresponding the user
                    extra_info_object = details_serializer(extra_info_object)       #passing it through the second serailizer
                    user_info = {}                                                  # declaring an empty dictionary
                    user_info['id']= user_object.data['id']                         #storing all teh necessary details one by one
                    user_info['first_name'] = user_object.data['first_name']
                    user_info['last_name'] = user_object.data['last_name']
                    user_info['username'] = user_object.data['username']
                    user_info['email'] = user_object.data['email']

                    user_info['gender'] = extra_info_object.data['gender']
                    user_info['phone_number'] = extra_info_object.data['phone_number']
                    user_info['address1'] = extra_info_object.data['address1']
                    user_info['address2'] = extra_info_object.data['address2']
                    user_info['city'] = extra_info_object.data['city']
                    user_info['state'] = extra_info_object.data['state']
                    user_info['country'] = extra_info_object.data['country']

                    user_list.append(user_info)                             #storing the dictionary in the list
                logger.info("all the users were displayed successfully")
                return Response(user_list, status=status.HTTP_201_CREATED)      #returning the list of all the user details in teh response
            else:
                logger.info("only an admin can use this API")
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while displaying users")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)

class ChangeUserStatus(viewsets.ModelViewSet):
    #this API is used to change the user's status from active to inactive and vice-versa
    @action(detail=True, methods=['get'])
    def user_status(self,request):
        try:
            token = request.headers['Authorization']
            if check_admin_token(token) == True:
                data = request.data
                user_id = data.get('user_id','')                    #getting the user_id from the post request
                user_status = data.get('status', '')                #getting the user_status, that needs to be changed from the post request
                if user_status == 'active' or user_status == 'inactive':      #this is to check that only 'active' or inactive' status is used and all the typos are handled in its else part
                    user_object = UserRegistrationModel.objects.get(id = user_id)       #now we get the object model using the user_id
                    user_object.is_active = user_status                                 # then we update its 'is_active' parameter with the user_sttus provided above
                    user_object.save(update_fields=['is_active'])
                    serializer = UserStatusSerializer                       # then we pass this object through a serialiazer that consists of 'is_active' field
                    user_object = serializer(user_object)
                    logger.info("user's status was updated successfully")
                    return Response({"success": (user_status_message_msg,user_object.data['is_active'])}, status=status.HTTP_200_OK)                #here we return that objects data
                else:
                    logger.info("invalid status was provided, hence an error")
                    return Response({"failure": wrong_status_msg}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while updating user's status")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)


class FlightsView(viewsets.ModelViewSet):
    serializer_class = FlightSerializer
    queryset = FlightModel.objects.all()


    def create(self, request):                        # here we pass flights details in the post request and it gets stored in the database
        try:
            token = request.headers['Authorization']
            if check_admin_token(token) == True:
                serializer = FlightSerializer(data=request.data)        # passing the flight's info through the serializer
                if serializer.is_valid():
                    serializer.save()                                   #saving it in the database
                    logger.info("flight in registered successfully")
                    return Response({"success": flight_success_msg},status=status.HTTP_201_CREATED)
            else:
                logger.info("only an admin can register flights")
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while registering a flight")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk):
        try:
            token = request.headers['Authorization']
            if check_admin_token(token) == True:
                data = request.data
                update_flights(data, pk)
                logger.info("flight info was updated successfully")
                return Response({'success': flight_update_success_msg}, status=status.HTTP_200_OK)
            else:
                logger.info("only an admin can update a flight's information")
                return Response({"failure": invalid_token_msg},status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while updating a flight's info")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            token = request.headers['Authorization']
            if check_admin_token(token) == True:
                data = request.data
                flight_id = data.get('flight_id', '')  # get the required flight_id from the post request
                flight_object = FlightModel.objects.get(id=flight_id)  # get the corresponding flight model object with that flight id
                flight_object.is_active = 'inactive'  # change its is_active permission to deactive, hence when we view only active flights, it looks like other flights deleted
                flight_object.save(update_fields=['is_active'])
                logger.info("flight was deleted successfully")
                return Response({"status": flight_delete_msg},status=status.HTTP_200_OK)  # success message if the flight is deleted
            else:
                logger.info("only an admin can access this API and delete flights")
                return Response({"failure": invalid_token_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while deleting a flight")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path="upload_image")             #by using an action decorater we use POST request in the URL flights/upload_image
    def upload_image(self, request):
        try:
            token = request.headers['Authorization']
            if check_admin_token(token) == True:
                serializer = ImageSerializer(data=request.data)         #data is passed in the serializer and saved in the database if it's valid
                if serializer.is_valid():
                    serializer.save()
                    logger.info("image was uploaded successfully")
                return Response({"status": image_uploaded_msg}, status=status.HTTP_200_OK)           # success message
            else:
                 logger.info("only an admin can access this API and upload an image")
                 return Response({"failure": invalid_token_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while uploading an image of the flight")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path="view_users")
    def all_users(self, request):
        try:
            token = request.headers['Authorization']
            if check_admin_token(token) == True:
                data = request.data
                file_format = data.get('file_format','')
                start_date = data.get('start_date', '')
                end_date = data.get('end_date', '')
                Status = data.get('status', '')

                if file_format == 'csv':
                    csv_file = create_user_csv(start_date, end_date, Status)
                    logger.info("CSV file of User Records was generated successfully")
                    return csv_file
                elif file_format == 'pdf':
                    pdf_file = create_user_pdf(start_date, end_date, Status)
                    logger.info("PDF file of User Records was generated successfully")
                    return pdf_file
                else:
                    logger.info("invalid file format was passed")
                    return Response({"failure": incorrect_file_format_msg},status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info("only an admin can access this API and get the required file")
                return Response({"failure": invalid_token_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while generating a CSV/PDF file")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path="view_flights/(?P<user_id>\d+)")
    def all_flights(self, request, user_id):
        try:
            token = request.headers['Authorization']
            if check_user_token(token) == True:
                data = request.data
                file_format = data.get('file_format', '')
                if file_format == 'csv':
                    csv_file = create_flight_csv(user_id)
                    logger.info("CSV file of User Flights was generated successfully")
                    return csv_file
                elif file_format == 'pdf':
                    pdf_file = create_flight_pdf(user_id)
                    logger.info("PDF file of User Flights was generated successfully")
                    return pdf_file
                else:
                    logger.info("invalid file format was passed")
                    return Response({"failure": incorrect_file_format_msg}, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info("only an admin can access this API and get the required file")
                return Response({"failure": invalid_token_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.info("error occurred while generating a CSV/PDF file")
            return Response({"failure": exception_msg}, status=status.HTTP_400_BAD_REQUEST)