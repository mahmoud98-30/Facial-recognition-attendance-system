from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext_lazy as _
from django.utils.translation.trans_null import ngettext_lazy

from account.forms import ProfileUpdateForm, StudentCreationForm, UpdateForm, LecturerCreationForm
from account.models import User
from attendance.forms import CourseForm, AttendanceForm
from attendance.models import Course, Attendance


@login_required(login_url='/login-page/')
def home(request):
    form_course = CourseForm(request.POST or None)
    form_attendance = AttendanceForm(request.POST or None)
    course = Attendance.objects.filter(student=request.user.id)
    attendance = Attendance.objects.all()

    if request.method == 'POST' and "course_form" in request.POST:
        if form_course.is_valid():
            form = form_course.save(commit=False)
            form.lecturer = request.user
            form.save()
            msg = 'done '
            messages.add_message(request, messages.SUCCESS, msg)
        form = CourseForm()
        print(request.POST)
        print(request.user)
        return render(request, 'index.html', {
            'form_course': form_course,
            'form_attendance': form_attendance,
            'course': course,
            'attendance': attendance,
        }, )

    elif request.method == 'POST' and "attendance" in request.POST:
        if form_attendance.is_valid():
            form = form_attendance.save(commit=False)
            form.student = request.user
            if Attendance.objects.filter(course=request.POST['course']).filter(student=request.user.id):
                msg = _(
                    'you are already registered in this course.')
                messages.add_message(request, messages.SUCCESS, msg)
                return HttpResponseRedirect("/")
            else:
                form.save()
                msg = 'done '
                messages.add_message(request, messages.SUCCESS, msg)
            form = AttendanceForm()
            course = Attendance.objects.filter(student=request.user.id)
            attendance = Attendance.objects.all()
            return render(request, 'index.html', {
                'form_course': form_course,
                'form_attendance': form_attendance,
                'course': course,
                'attendance': attendance,
            }, )
    return render(request, 'index.html', {
        'form_course': form_course,
        'form_attendance': form_attendance,
        'course': course,
        'attendance': attendance,
    }, )


def login_page(request):
    return render(request, 'login_page.html', {

    }, )


def student_register(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password1'])
            username = form.cleaned_data.get('username')
            new_user.is_student = True
            new_user.save()
            msg = _(
                f'Congratulations {username} Your registration has been completed successfully.')
            messages.add_message(request, messages.SUCCESS, msg)
            return redirect('/student-login/')
    else:
        form = StudentCreationForm()
    return render(request, 'account/student/register.html', {
        'title': _('register'),
        'form': form,
    }, )


def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            msg = _('There is an error in the index number or password')
            messages.add_message(request, messages.WARNING, msg)
    return render(request, 'account/student/login.html', {
        'title': _('Login'),
    })


def user_logout(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/student-login/')
def student_profile_update(request):
    if request.method == 'POST':
        user_form = UpdateForm(request.POST, instance=request.user)
        if user_form.is_valid:
            user_form.save()

            msg = _('Modified successfully.')
            messages.add_message(request, messages.SUCCESS, msg)

            return redirect('/student-profile-update/')
    else:
        user_form = UpdateForm(instance=request.user)

    context = {
        'title': _('profile update'),
        'user_form': user_form,
    }
    return render(request, 'account/student/profile.html', context)


def lecturer_register(request):
    if request.method == 'POST':
        form = LecturerCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password1'])
            username = form.cleaned_data.get('username')
            new_user.is_lecturer = True
            new_user.save()
            msg = _(
                f'Congratulations {username} Your registration has been completed successfully.')
            messages.add_message(request, messages.SUCCESS, msg)
            return redirect('/lecturer-login/')
    else:
        form = LecturerCreationForm()
    return render(request, 'account/lecturer/register.html', {
        'title': _('register'),
        'form': form,
    }, )


def lecturer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            username = get_object_or_404(User, email=email)
        except :
            msg = _('There is an error in the index number or password')
            messages.add_message(request, messages.WARNING, msg)
            return HttpResponseRedirect('/lecturer-login/')
        if username:
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                msg = _('There is an error in the index number or password')
                messages.add_message(request, messages.WARNING, msg)
        else:
            msg = _('There is an error in the index number or password')
            messages.add_message(request, messages.WARNING, msg)
            return HttpResponseRedirect('/')

    return render(request, 'account/lecturer/login.html', {
        'title': _('Login'),
    })


@login_required(login_url='/lecturer-login/')
def lecturer_profile_update(request):
    if request.method == 'POST':
        user_form = UpdateForm(request.POST, instance=request.user)
        if user_form.is_valid:
            user_form.save()

            msg = _('Modified successfully.')
            messages.add_message(request, messages.SUCCESS, msg)

            return redirect('/lecturer-profile-update/')
    else:
        user_form = UpdateForm(instance=request.user)

    context = {
        'title': _('profile update'),
        'user_form': user_form,
    }
    return render(request, 'account/lecturer/profile.html', context)
