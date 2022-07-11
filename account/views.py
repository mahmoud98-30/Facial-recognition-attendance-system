import username as username
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext_lazy as _
from django.utils.translation.trans_null import ngettext_lazy

from account.forms import ProfileUpdateForm, StudentCreationForm, UpdateForm, LecturerCreationForm
from account.models import User


@login_required(login_url='/login-page/')
def home(request):
    return render(request, 'index.html', {

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
    return redirect('/student-login/')


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
            return redirect('/student-login/')
    else:
        form = LecturerCreationForm()
    return render(request, 'account/lecturer/register.html', {
        'title': _('register'),
        'form': form,
    }, )


def lecturer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = User.objects.get(email=email)
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            msg = _('There is an error in the index number or password')
            messages.add_message(request, messages.WARNING, msg)
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
