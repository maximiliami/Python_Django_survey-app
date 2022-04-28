from django.contrib import admin
from questionnaire.models import *
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    search_fields = ('user_code',)
    ordering = ('-start_date',)
    list_display = ('user_code', 'is_active', 'is_staff')
    list_filter = ('pair', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('user_code',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Pair', {'fields': ('pair',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_code', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )


# Register your models here.
admin.site.register(Pair)
admin.site.register(PseudoUser, UserAdminConfig)
admin.site.register(QuestionnaireStart)
admin.site.register(QuestionnaireEnd)
admin.site.register(QuestionnaireDaily)
