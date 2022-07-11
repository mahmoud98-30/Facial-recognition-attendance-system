from django.contrib import admin
from django.contrib.auth import get_user_model

from account.models import Profile

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'is_superuser', 'is_student', 'is_lecturer']
    search_fields = ['username', 'first_name']
    list_filter = ('is_student', 'is_lecturer')


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', ]


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
