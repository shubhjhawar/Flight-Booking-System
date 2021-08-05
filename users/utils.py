from datetime import datetime
import jwt
from .models import UserRegistrationModel, UserRegistrationDetailModel, FlightModel, UserFlightModel
import csv
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT,TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter

secret = 'SECRET_KEY'

def time_allowed(token):                    #this function is to used to calculate the time allowed
    date_and_time = token["valid_time"]
    date, time = date_and_time.split()
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = time[:2]
    minute = time[3:5]
    valid_time = int(year+month+day+hour+minute)
    return valid_time


def time():                             #this function is used to calculate the current time
    date1 = str(datetime.now())
    date, time = date1.split()
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = time[:2]
    minute = time[3:5]
    current_time = int(year + month + day + hour + minute)
    return current_time

def is_admin(token):            # this function is used to check if an admin is operating or not
    token = jwt.decode(token, secret, algorithms=["HS256"])
    role = token['role']
    if role == 'admin':
        return True
    else:
        return False

def is_valid_token(token):            # this function s used to check if the tkoen provided is valid or not
    token = jwt.decode(token, secret, algorithms=["HS256"])
    valid_time = time_allowed(token)
    current_time = time()

    if current_time <= valid_time:
        return True
    else:
        return False


def check_user_token(token):        #this funtion is used to check if the token is valid and an user is operating
    if is_valid_token(token) == True and is_admin(token) == False:
        return True
    else:
        return False


def check_admin_token(token):       #this funtion is used to check if the token is valid and an admin is operating
    if is_valid_token(token) == True and is_admin(token) == True:
        return True
    else:
        return False


def update_basic_details(data):
    # fetching data one by one and storing it into variables
    user_id = data.get('user_id', '')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    basic_info = UserRegistrationModel.objects.get(id=user_id)
    if len(last_name) != 0:  # if last_name is provided
        basic_info.last_name = last_name  # last_name is changed from the model's object
        basic_info.save(update_fields=['last_name'])  # and then it is updated

    if len(first_name) != 0:  # if first_name field is provided, it gets updated
        basic_info.first_name = first_name
        basic_info.save(update_fields=['first_name'])

    basic_info.save()

def update_extra_details(data):
    # fetching data one by one and storing it into variables
    user_id = data.get('user_id', '')
    gender = data.get('gender', '')
    address1 = data.get('address1', '')
    address2 = data.get('address2', '')
    city = data.get('city', '')
    state = data.get('state', '')
    country = data.get('country', '')
    phone_number = data.get('phone_number', '')

    extra_info = UserRegistrationDetailModel.objects.get(user_info=user_id)
    if len(city) != 0:  # if city is provied
        extra_info.city = city  # city from the model is changed
        extra_info.save(update_fields=['city'])  # city is updated in that specific model object
    if len(gender) != 0:  # if gender field is provided, it gets updated
        extra_info.gender = gender
        extra_info.save(update_fields=['gender'])
    if len(address1) != 0:  # if address1 and address2 field are provided, it gets updated
        extra_info.address1 = address1
        extra_info.save(update_fields=['address1'])
    if len(address2) != 0:
        extra_info.address2 = address2
        extra_info.save(update_fields=['address2'])
    if len(state) != 0:  # if city adn country field are provided, it gets updated
        extra_info.state = state
        extra_info.save(update_fields=['state'])
    if len(country) != 0:
        extra_info.country = country
        extra_info.save(update_fields=['phone_number'])
    if len(phone_number) != 0:  # if phone_number field is provided, it gets updated
        extra_info.phone_number = phone_number
        extra_info.save(update_fields=['phone_number'])

    extra_info.modified_date = datetime.now()
    extra_info.save()


def update_flights(data, pk):
    # fetching data one by one and storing it into variables
    flight_id = pk  # pk = primary key passeed in the URL which works as the flight_id that needs to be updated
    company = data.get('company', '')
    arrival = data.get('arrival', '')
    departure = data.get('departure', '')
    distance = data.get('distance', '')
    price = data.get('price', '')

    flight_info = FlightModel.objects.get(id=flight_id)  # object of that user from the table 1(basic info)

    if len(company) != 0:  # if the company field is provided
        flight_info.company = company  # company of that flight would be changed
        flight_info.save(update_fields=['company'])
    if len(arrival) != 0:
        flight_info.arrival = arrival
        flight_info.save(update_fields=['arrival'])
    if len(departure) != 0:
        flight_info.departure = departure
        flight_info.save(update_fields=['departure'])
    if len(distance) != 0:
        flight_info.distance = distance
        flight_info.save(update_fields=['distance'])
    if len(price) != 0:
        flight_info.price = price
        flight_info.save(update_fields=['price'])

    flight_info.save()  # updated object model would be saved in the database


def create_user_csv(start_date,end_date,Status):
    csv_file_name = 'user_records_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.csv'
    # creating a csv type response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + csv_file_name
    writer = csv.writer(response)
    # this first row is hard-coded and is used as column headings
    writer.writerow(
        ['S no.', 'first_name', 'last_name', 'username', 'email', 'role', 'is_active', 'gender', 'phone_number',
         'address1', 'address2', 'city', 'state', 'country', 'date_joined', 'modified_date'])
    # all the model objects consisting of user's basic and extra information is fetched
    objects = UserRegistrationDetailModel.objects.filter(date_joined__range=[start_date, end_date])
    counter = 1
    # using a for loop, we put all the details of a user in a list and write that list in the CSV file
    for object in objects:
        primary_details = UserRegistrationModel.objects.get(id=object.id)
        if primary_details.is_active == Status:
            user_details = [counter, primary_details.first_name, primary_details.last_name,
                            primary_details.username, primary_details.email, primary_details.role,
                            primary_details.is_active, object.gender, object.phone_number, object.address1,
                            object.address2, object.city, object.state, object.country, object.date_joined,
                            object.modified_date]
            writer.writerow(user_details)
            counter+=1
    # CSV file is generated successfully and returned
    return response

def create_user_pdf(start_date,end_date,Status):
    pdf_file_name = 'user_records_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.pdf'
    # creating a pdf type response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename =' + pdf_file_name
    # data-list is first hardcoded with column names
    data = [
        ['S no.', 'first_name', 'last_name', 'username', 'email', 'role', 'is_active', 'gender', 'phone_number',
         'address1', 'address2', 'city', 'state', 'country', 'date_joined', 'modified_date']
    ]
    # using a for loop, all the necessary details od a user is fetched and then appended in the data-list
    objects = UserRegistrationDetailModel.objects.filter(date_joined__range=[start_date, end_date])
    counter = 1
    for object in objects:
        primary_details = UserRegistrationModel.objects.get(id=object.id)
        if primary_details.is_active == Status:
            user_details = [counter, primary_details.first_name, primary_details.last_name,
                            primary_details.username, primary_details.email,
                            primary_details.role, primary_details.is_active, object.gender, object.phone_number,
                            object.address1,
                            object.address2, object.city, object.state, object.country, object.date_joined,
                            object.modified_date]
            data.append(user_details)
            counter+=1
    # response(PDF) is put under filename
    filename = response
    # this filename and the size of pdf is passed in the SimpleDocTemplate
    pdf = SimpleDocTemplate(
        filename,
        pagesize=(16 * inch, 10 * inch)
    )
    # logo of the company on the top right corner
    logo = Image('static/logo/logo.png', 1.5 * inch, 1.5 * inch, hAlign='RIGHT')
    # heading for the pdf, used as a paragraph and styled accordingly
    heading = "User Records".replace('\n', '<br />\n')
    heading_style = ParagraphStyle(
        name='Normal',
        fontSize=17,
        alignment=TA_LEFT,
    )
    dates = "Start Date: " + start_date + "<br />\n" + "End Date: " + end_date + "&nbsp <br />\n".replace('\n',
                                                                                                          '<br />\n')
    date_style = ParagraphStyle(
        name='Normal',
        fontSize=13,
        alignment=TA_RIGHT,
    )
    # then a table is declared, data from the data-list is put into the table and it is styled accordingly
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (15, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    # an empty list-elements is declared, heading ad table is appended to it
    elements = []
    elements.append(logo)
    elements.append(Paragraph(heading, style=heading_style))
    elements.append(Paragraph(dates, style=date_style))
    elements.append(table)
    # the pdf is built through this elements-list
    pdf.build(elements)
    return response

def create_flight_csv(user_id):
    csv_file_name = 'user_flights_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.csv'
    # creating a csv type response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + csv_file_name
    writer = csv.writer(response)
    # this first row is hard-coded and is used as column headings
    writer.writerow(['S no.','company', 'distance', 'arrival', 'departure', 'price', 'date_of_booking'])
    objects = UserFlightModel.objects.filter(user_info=user_id)
    counter = 1
    for object in objects:
        flight_details = object.flight_info
        details = [counter,flight_details.company, flight_details.distance, flight_details.arrival,
                   flight_details.departure, flight_details.price, object.date_of_booking]
        writer.writerow(details)
        counter+=1
    return response

def create_flight_pdf(user_id):
    pdf_file_name = 'user_flights_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.pdf'
    # creating a pdf type response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename =' + pdf_file_name
    # data-list is first hardcoded with column names
    data = [['S no.','company', 'distance', 'arrival', 'departure', 'price', 'date_of_booking']]
    objects = UserFlightModel.objects.filter(user_info=user_id)
    counter = 1
    for object in objects:

        flight_details = object.flight_info
        details = [counter, flight_details.company, flight_details.distance, flight_details.arrival,
                   flight_details.departure, flight_details.price, object.date_of_booking]
        data.append(details)
        counter+=1
    # response(PDF) is put under filename
    filename = response
    # this filename and the size of pdf is passed in the SimpleDocTemplate
    pdf = SimpleDocTemplate(
        filename,
        pagesize=letter
    )
    # logo of the company on the top right corner
    logo = Image('static/logo/logo.png', 1.5 * inch, 1.5 * inch, hAlign='RIGHT')
    # heading for the pdf, used as a paragraph and styled accordingly
    heading = "&nbsp &nbsp &nbsp &nbsp &nbsp User Flights <br />\n".replace('\n', '<br />\n')
    heading_style = ParagraphStyle(
        name='Normal',
        fontSize=17,
        alignment=TA_LEFT,
    )
    # then a table is declared, data from the data-list is put into the table and it is styled accordingly
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (15, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    # an empty list-elements is declared, heading ad table is appended to it
    elements = []
    elements.append(logo)
    elements.append(Paragraph(heading, style=heading_style))
    elements.append(table)
    # the pdf is built through this elements-list
    pdf.build(elements)
    return response