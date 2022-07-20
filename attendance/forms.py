from django import forms

from attendance.models import Course, Attendance


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name',)


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ('course',)

    def clean_data(request, self):

        cd = self.cleaned_data
        if Attendance.objects.filter(course=cd['course']).filter(student=request.user.id):
            raise forms.ValidationError("The phone is already exist!")
        return cd['course']

