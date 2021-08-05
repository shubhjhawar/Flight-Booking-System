from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, LoginView,UserProfileView, UserProfileUpdateView,ChangePasswordView,FlightView, BookFlightView,UserInfoView,ChangeUserStatus, FlightsView, ActivateAccount
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('flights', FlightsView, basename='flights')

urlpatterns = [
    path('register',RegisterView.as_view()),
    path('login',LoginView.as_view()),
    path('profile',UserProfileView.as_view()),
    path('profile/update',UserProfileUpdateView.as_view()),
    path('change_password',ChangePasswordView.as_view()),
    path('flights',FlightView.as_view()),
    path('flights/book',BookFlightView.as_view()),
    path('flights/book/<int:user_id>',BookFlightView.as_view()),
    path('all_users',UserInfoView.as_view()),
    path('change_status',ChangeUserStatus.as_view({"post": "user_status"})),
    path('', include(router.urls)),
    path('activate/<code>',ActivateAccount.as_view(), name='activate'),
]