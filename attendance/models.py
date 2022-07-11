from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Course(models.Model):
    name = models.CharField(_("Course Name"), max_length=255)
    lecturer = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name="Lecturer",
                                 verbose_name=_("User"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Course")


class Attendance(models.Model):
    student = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name="Student",
                                verbose_name=_("User"))
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name="CourseName",
                               verbose_name=_("Course"))
    is_present = models.BooleanField(default=False, verbose_name=_("Is Present"))

    def __str__(self):
        return self.student.username

    class Meta:
        verbose_name = _("Attendance")
