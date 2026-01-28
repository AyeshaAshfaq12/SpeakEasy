from django.urls import path
from . import views

# Password Reset Imports
from django.contrib.auth import views as auth_views

urlpatterns = [

    # Authentication
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout'),


    # Password Reset URLS
    path( 'password_reset/' ,auth_views.PasswordResetView.as_view(),name='password_reset'),
    path( 'password_reset/done/', auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),


    # General Routes
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    

    # Meeting
    path('rooms/create/', views.lobby, name='create_room'),
    path('room/', views.room, name='room'),
    path('room/<str:meeting_id>/', views.join_room_with_link, name='join_room_with_link'),
    path('rooms/join/', views.join_room, name='join_room'),


    # Pricing Routes
    path('pricing/', views.pricing, name='pricing'),


    # Pre-Meeting Helpers
    path('get_token/', views.get_token, name='get_token'),


    # Agora Helper Functions
    path('get_member/', views.get_member, name='get_member'),
    path('create_member/', views.create_member, name="create_member"),
    path('delete_member/', views.delete_member, name="delete_member"),

    # Live Transcription Routes
    path('upload_audio/', views.upload_audio, name="upload_audio"),


]