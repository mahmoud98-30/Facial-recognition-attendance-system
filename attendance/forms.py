from django import forms
from django.forms import widgets

from attendance.models import Course, Attendance


class CourseForm(forms.ModelForm):
    date = forms.DateField(widget=widgets.DateInput,)
    time = forms.TimeField(widget=widgets.TimeInput,)
    class Meta:
        model = Course
        fields = ('name', 'date', 'time')


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ('course',)

    def clean_data(request, self):

        cd = self.cleaned_data
        if Attendance.objects.filter(course=cd['course']).filter(student=request.user.id):
            raise forms.ValidationError("The phone is already exist!")
        return cd['course']

