from django.urls import path
from .views import signup_view, signin_view, logout_view
from django.contrib.auth import views as auth_views
from .views import request_password_reset, reset_password, reset_password_done, reset_password_complete
from .views import send_sos_email
from .views import main_home ,about, services, contact, user_profile
from .views import track_view
from django.urls import path
from .views import add_contact, get_contacts, remove_contact
from django.urls import path
from .views import save_voice_command, get_voice_command

from .views import join_us
   

urlpatterns = [

    path('signup/', signup_view, name='signup'),
    path('signin/', signin_view, name='signin'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', request_password_reset, name='password_reset'),
    path('password-reset/done/', reset_password_done, name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='password_reset_confirm'),
    path('password-reset-complete/', reset_password_complete, name='password_reset_complete'),
    path("send-sos/", send_sos_email, name="send_sos_email"),
 path("save-voice-command/", save_voice_command, name="save_voice_command"),
    path("get-voice-command/<int:user_id>/", get_voice_command, name="get_voice_command"),
    path('live-track/<int:user_id>/', track_view, name='track'),
    path('main-home/', main_home, name='home'),
    path('about/', about, name='about'),
    path('services/', services, name='services'),
    path('contact/', contact, name='contact'),
    path('profile/', user_profile, name='user_profile'),  
    path("add-contact/", add_contact, name="add_contact"),
    path("get-contacts/<int:user_id>/", get_contacts, name="get_contacts"),
    path("remove-contact/", remove_contact, name="remove_contact"),

    path('', join_us, name='joinus'),
   
]

# from django.urls import path, include

# urlpatterns = [
#     path('auth/', include('social_django.urls', namespace='social')),
# ]
