from pyexpat.errors import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView

from attendance.forms import CourseForm
from attendance.models import Course, Attendance


class CourseUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Course
    template_name = 'attendance/course_update.html'
    form_class = CourseForm

    def form_valid(self, form):
        form.instance.lecturer = self.request.user
        return super().form_valid(form)

    def test_func(self):
        course = self.get_object()
        if self.request.user == course.lecturer:
            return True
        else:
            return False


class CourseDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Course
    success_url = '/'

    def test_func(self):
        course = self.get_object()
        if self.request.user == course.lecturer:
            return True
        else:
            return False


@login_required(login_url='/student-login/')
def return_course(request, id):
    Attendance.objects.get(id=id).delete()
    return HttpResponseRedirect("/")


@login_required(login_url='/student-login/')
def register_in_course(request, id):
    course = Course.objects.get(id=id)
    t = Attendance(student=request.user, course=course)
    t.save()
    return HttpResponseRedirect("/")


@login_required(login_url='/student-login/')
def attendance(request):

    return render(request, 'attendance/attendance.html', {

    }, )
