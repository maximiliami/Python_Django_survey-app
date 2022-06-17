from django.contrib.auth.forms import UserCreationForm

import questionnaire.models


# overrides the UserCreationForm so that it is possible to create a PseudoUser
class RegisterForm(UserCreationForm):
    class Meta:
        model = questionnaire.models.PseudoUser
        fields = ['user_code', 'gender', 'pair']
