from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.forms import ModelForm as CModelForm

from questionnaire.models import PseudoUser, Question, Choice
from service.services import Service


# overrides the UserCreationForm so that it is possible to create a PseudoUser
class RegisterForm(UserCreationForm):
    class Meta:
        model = PseudoUser
        fields = ['user_code', 'pair']

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


class QuestionForm(CModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        exclude = ('question_catalogue',)


class ChoiceForm(CModelForm):
    class Meta:
        model = Choice
        fields = '__all__'


QuestionChoiceFormset = inlineformset_factory(Question, Choice,
                                              fields=['question', 'choice_text', 'value', ],
                                              extra=7,
                                              max_num=7,
                                              can_delete=True, )

