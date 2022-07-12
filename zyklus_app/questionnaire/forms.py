from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm

from questionnaire.models import PseudoUser, QuestionnaireStart
from service.services import Service


# overrides the UserCreationForm so that it is possible to create a PseudoUser


class RegisterForm(UserCreationForm):
    class Meta:
        model = PseudoUser
        fields = ['user_code', 'gender', 'pair']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        open_pairs = Service.get_open_pairs()
        self.fields['pair'].queryset = open_pairs


class UpdateUserForm(UserChangeForm):
    password = None

    class Meta:
        model = PseudoUser
        fields = ['user_code', 'gender', 'pair']

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        open_pairs = Service.get_open_pairs()
        self.fields['pair'].queryset = open_pairs


class QuestionnaireStartForm(ModelForm):
    class Meta:
        model = QuestionnaireStart
        fields = '__all__'
        exclude = ('pseudo_user',)
