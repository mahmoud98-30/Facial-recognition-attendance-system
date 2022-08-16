from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from account.views import *
from attendance.views import CourseUpdateView, CourseDeleteView, register_in_course, return_course, attendance, \
    attendance_in, edit_attendance

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
    path('edit-attendance/', edit_attendance, name='edit-attendance'),

    path('logout/', user_logout, name='logout'),

    path('detail/<slug:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('detail/<slug:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),

    path('register/<int:id>/', register_in_course, name='register-course'),
    path('return/<int:id>/', return_course, name='return-course'),

    path('attendance-course/', attendance, name='attendance-course'),
    path('attendance-in/<int:course>/', attendance_in, name='attendance-in'),

    path('train/', train, name='train'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
