from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


# introduces PseudoUserModel to the admin-interface
class UserAdminConfig(UserAdmin):
    search_fields = ('user_code',)
    ordering = ('-start_date',)
    list_display = ('user_code', 'is_active', 'is_staff')
    list_filter = ('pair', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('user_code', 'password')}),
        ('Permissions',
         {'fields': ('groups', 'is_staff', 'is_active', 'is_superuser')}),
        ('Pair', {'fields': ('pair',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_code', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
         ),
    )

    # disables the configuration-form for PseudoUser if not Superuser
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['is_staff'].disabled = True
            form.base_fields['is_active'].disabled = True
            form.base_fields['groups'].disabled = True
            form.base_fields['user_code'].disabled = True
            form.base_fields['pair'].disabled = True
        return form


# Register your models here.
admin.site.register(Pair)
admin.site.register(PseudoUser, UserAdminConfig)
admin.site.register(QuestionnaireStart)
admin.site.register(QuestionnaireEnd)
admin.site.register(QuestionnaireDaily)
