from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
import questionnaire.models


# overrides the UserCreationForm so that it is possible to create a PseudoUser
class RegisterForm(UserCreationForm):
    class Meta:
        model = questionnaire.models.PseudoUser
        fields = ['user_code', 'gender', 'pair']


class QuestionnaireStartForm(ModelForm):
    class Meta:
        model = questionnaire.models.QuestionnaireStart
        fields = '__all__'
        exclude = ('pseudo_user',)

