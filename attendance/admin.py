from django.contrib import admin

from attendance.models import Course, Attendance


class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'lecturer', ]
    search_fields = ['name', 'lecturer__username', ]


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'is_present', ]
    search_fields = ['student__username', 'course__name', ]
    list_filter = ('is_present',)


admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance, AttendanceAdmin)
