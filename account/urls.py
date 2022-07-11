from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from account.views import *

app_name = 'account'
urlpatterns = [
    path('', home, name='home'),
    path('login-page/', login_page, name='login-page'),

    path('student-register/', student_register, name='student-register'),
    path('student-login/', student_login, name='student-login'),
    path('student-profile-update/', student_profile_update, name='student-profile-update'),

    path('lecturer-register/', lecturer_register, name='lecturer-register'),
    path('lecturer-login/', lecturer_login, name='lecturer-login'),
    path('lecturer-profile-update/', lecturer_profile_update, name='lecturer-profile-update'),

    path('logout/', user_logout, name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
