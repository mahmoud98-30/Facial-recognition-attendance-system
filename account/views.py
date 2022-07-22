import os
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
import dlib
import cv2
import imutils
from imutils import face_utils
from imutils.video import VideoStream
from imutils.face_utils import rect_to_bb
from imutils.face_utils import FaceAligner

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


def create_dataset(username):
    id = username
    if not os.path.exists('account/face_recognition_data/training_dataset/{}/'.format(id)):
        os.makedirs('account/face_recognition_data/training_dataset/{}/'.format(id))
    directory = 'account/face_recognition_data/training_dataset/{}/'.format(id)

    # Detect face
    # Loading the HOG face detector and the shape predictpr for allignment

    print("[INFO] Loading the facial detector")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(
        'face_recognition_data/shape_predictor_68_face_landmarks.dat')  # Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
    fa = FaceAligner(predictor, desiredFaceWidth=96)
    # capture images from the webcam and process and detect the face
    # Initialize the video stream
    print("[INFO] Initializing Video stream")
    vs = VideoStream(src=0).start()
    # time.sleep(2.0) ####CHECK######

    # Our identifier
    # We will put the id here and we will store the id with a face, so that later we can identify whose face it is

    # Our dataset naming counter
    sampleNum = 0
    # Capturing the faces one by one and detect the faces and showing it on the window
    while True:
        # Capturing the image
        # vs.read each frame
        frame = vs.read()
        # Resize each image
        frame = imutils.resize(frame, width=800)
        # the returned img is a colored image but for the classifier to work we need a greyscale image
        # to convert
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # To store the faces
        # This will detect all the images in the current frame, and it will return the coordinates of the faces
        # Takes in image and some other parameter for accurate result
        faces = detector(gray_frame, 0)
        # In above 'faces' variable there can be multiple faces so we have to get each and every face and draw a
        # rectangle around it.

        for face in faces:
            print("inside for loop")
            (x, y, w, h) = face_utils.rect_to_bb(face)

            face_aligned = fa.align(frame, gray_frame, face)
            # Whenever the program captures the face, we will write that is a folder
            # Before capturing the face, we need to tell the script whose face it is
            # For that we will need an identifier, here we call it id
            # So now we captured a face, we need to write it in a file
            sampleNum = sampleNum + 1
            # Saving the image dataset, but only the face part, cropping the rest

            if face is None:
                print("face is none")
                continue

            cv2.imwrite(directory + '/' + str(sampleNum) + '.jpg', face_aligned)
            face_aligned = imutils.resize(face_aligned, width=400)
            # cv2.imshow("Image Captured",face_aligned)
            # @params the initial point of the rectangle will be x,y and
            # @params end point will be x+width and y+height
            # @params along with color of the rectangle
            # @params thickness of the rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
            # Before continuing to the next loop, I want to give it a little pause
            # waitKey of 100 millisecond
            cv2.waitKey(50)

        # Showing the image in another window
        # Creates a window with window name "Face" and with the image img
        cv2.imshow("Add Images", frame)
        # Before closing it we need to give a wait command, otherwise the open cv wont work
        # @params with the millisecond of delay 1
        cv2.waitKey(1)
        # To get out of the loop
        if (sampleNum > 300):
            break

    # Stoping the videostream
    vs.stop()
    # destroying all the windows
    cv2.destroyAllWindows()


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
