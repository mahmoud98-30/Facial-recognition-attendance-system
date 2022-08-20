import face_recognition
from imutils import face_utils
from imutils.video import VideoStream
from imutils.face_utils import FaceAligner
import time
from sklearn.preprocessing import LabelEncoder
import datetime
import pickle
import dlib
import cv2
import imutils
import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView

from account.admin import User
from attendance.forms import CourseForm
from attendance.models import Course, Attendance


class CourseUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Course
    template_name = 'attendance/course_update.html'
    form_class = CourseForm
    success_url = '/'

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

    msg = 'returned the course'
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect("/")


@login_required(login_url='/student-login/')
def register_in_course(request, id):
    course = Course.objects.get(id=id)
    t = Attendance(student=request.user, course=course)
    t.save()
    msg = 'Done'
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect("/")


@login_required(login_url='/student-login/')
def attendance(request):
    course = Attendance.objects.filter(student=request.user.id)
    return render(request, 'attendance/attendance.html', {
        'course': course

    }, )


def predict(face_aligned, svc, threshold=0.7):
    face_encodings = np.zeros((1, 128))
    try:
        x_face_locations = face_recognition.face_locations(face_aligned)
        faces_encodings = face_recognition.face_encodings(face_aligned, known_face_locations=x_face_locations)
        if (len(faces_encodings) == 0):
            return ([-1], [0])

    except:

        return ([-1], [0])

    prob = svc.predict_proba(faces_encodings)
    result = np.where(prob[0] == np.amax(prob[0]))
    if (prob[0][result[0]] <= threshold):
        return ([-1], prob[0][result[0]])

    return (result[0], prob[0][result[0]])


def update_attendance(request, present, id):
    for person in present:
        print(person)
        student = User.objects.get(username=person)
        if student == request.user:
            print(student == request.user)
            try:
                qc = Course.objects.get(id=id)
            except:
                qc = None
            try:
                qs = Attendance.objects.get(student=student, course=qc)
            except:
                qs = None

            if qs is None:
                if present[person] == True:
                    a = Attendance(student=student, course=qc, is_present=True)
                    a.save()
                    msg = (
                        'done')
                    messages.add_message(request, messages.SUCCESS, msg)
                else:
                    a = Attendance(student=student, course=qc, is_present=False)
                    a.save()
            else:
                if present[person] == True:
                    qs.is_present = True
                    qs.save(update_fields=['is_present'])
                    msg = (
                        'done')
                    messages.add_message(request, messages.SUCCESS, msg)

        else:
            print(student == request.user)
            msg = (
                'it,s not same')
            messages.add_message(request, messages.WARNING, msg)


def attendance_in(request, course):
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor(
        'account/face_recognition_data/shape_predictor_68_face_landmarks.dat')  # Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
    svc_save_path = "account/face_recognition_data/svc.sav"

    with open(svc_save_path, 'rb') as f:
        svc = pickle.load(f)
    fa = FaceAligner(predictor, desiredFaceWidth=96)
    encoder = LabelEncoder()
    encoder.classes_ = np.load('account/face_recognition_data/classes.npy')

    faces_encodings = np.zeros((1, 128))
    no_of_faces = len(svc.predict_proba(faces_encodings)[0])
    count = dict()
    present = dict()
    log_time = dict()
    start = dict()
    for i in range(no_of_faces):
        count[encoder.inverse_transform([i])[0]] = 0
        present[encoder.inverse_transform([i])[0]] = False

    vs = VideoStream(src=0).start()

    sampleNum = 0

    while (True):

        frame = vs.read()

        frame = imutils.resize(frame, width=800)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray_frame, 0)

        for face in faces:
            print("INFO : inside for loop")
            (x, y, w, h) = face_utils.rect_to_bb(face)

            face_aligned = fa.align(frame, gray_frame, face)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

            (pred, prob) = predict(face_aligned, svc)

            if (pred != [-1]):

                person_name = encoder.inverse_transform(np.ravel([pred]))[0]
                pred = person_name
                if count[pred] == 0:
                    start[pred] = time.time()
                    count[pred] = count.get(pred, 0) + 1

                if count[pred] == 4 and (time.time() - start[pred]) > 1.2:
                    count[pred] = 0
                else:
                    # if count[pred] == 4 and (time.time()-start) <= 1.5:
                    present[pred] = True
                    log_time[pred] = datetime.datetime.now()
                    count[pred] = count.get(pred, 0) + 1
                    print(pred, present[pred], count[pred])
                cv2.putText(frame, str(person_name) + str(prob), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1)

            else:
                person_name = "unknown"
                cv2.putText(frame, str(person_name), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # cv2.putText()
        # Before continuing to the next loop, I want to give it a little pause
        # waitKey of 100 millisecond
        # cv2.waitKey(50)

        # Showing the image in another window
        # Creates a window with window name "Face" and with the image img
        cv2.imshow("Mark Attendance - In - Press q to exit", frame)
        # Before closing it we need to give a wait command, otherwise the open cv wont work
        # @params with the millisecond of delay 1
        # cv2.waitKey(1)
        # To get out of the loop
        key = cv2.waitKey(50) & 0xFF
        if (key == ord("q")):
            break

    # Stoping the videostream
    vs.stop()

    # destroying all the windows
    cv2.destroyAllWindows()
    print(course)
    update_attendance(request, present, course)
    print(present)
    return redirect('/attendance-course/')


def edit_attendance(request):
    course = Attendance.objects.filter(course__lecturer=request.user.id)
    return render(request, 'attendance/edit_attendance.html', {
        'course': course

    }, )


def edit_attendance_in(request, course, student):
    q_course = Course.objects.get(id=course)
    q_student = User.objects.get(id=student)
    q_attendance = Attendance.objects.get(student=q_student, course=q_course)
    q_attendance.is_present = True
    q_attendance.save(update_fields=['is_present'])
    msg = (
        'done')
    messages.add_message(request, messages.SUCCESS, msg)
    return redirect('/edit-attendance/')


def edit_attendance_out(request, course, student):
    q_course = Course.objects.get(id=course)
    q_student = User.objects.get(id=student)
    q_attendance = Attendance.objects.get(student=q_student, course=q_course)
    q_attendance.is_present = False
    q_attendance.save(update_fields=['is_present'])
    msg = (
        'done')
    messages.add_message(request, messages.SUCCESS, msg)
    return redirect('/edit-attendance/')
