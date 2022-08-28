from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
# Create your models here.
from questionnaire import choices


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, user_code, password, **other_fields):
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser muss folgenden Wert erhalten: is_superuser=True')
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser muss folgenden Wert erhalten: is_staff=True')

        return self.create_user(user_code, password, **other_fields)

    def create_user(self, user_code, password, **other_fields):  #

        other_fields.setdefault('is_staff', True)

        if not user_code:
            raise ValueError(_('Sie müssen Ihren User-Code eingeben'))

        user = self.model(user_code=user_code, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Pair(models.Model):
    """Forms a pair of persons"""
    ident = models.CharField(_('Paar'), max_length=10, unique=True)

    def __str__(self):
        return self.ident


class PseudoUser(AbstractBaseUser, PermissionsMixin):
    user_code = models.CharField(_('Persönlicher Code'), max_length=10, unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(_('Geschlecht'), max_length=6, choices=choices.GENDER_CHOICES, default='Null', null=True)
    objects = CustomAccountManager()

    USERNAME_FIELD = 'user_code'

    def __str__(self):
        return self.user_code


class QuestionCatalogue(models.Model):
    name = models.CharField(max_length=25, choices=choices.QUESTIONNAIRE_CHOICES, default='None',
                            unique='True')

    def __str__(self):
        return str(self.name)

    def get_all_questions(self):
        return Question.objects.filter(question_catalogue__exact=self)


# Models for editable Questions
class Question(models.Model):
    name = models.CharField(_('Identifikator'), max_length=10, default='', unique='True')
    question_text = models.CharField(_('Frage Text'), max_length=200)
    hidden = models.BooleanField(_('Frage versteckt?'), default='False')
    show_at_question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, blank=True)
    question_catalogue = models.ForeignKey(QuestionCatalogue, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.question_text)

    def get_all_choices(self):
        return Choice.objects.filter(question=self)

    def get_absolute_url(self):
        return reverse('questionnaire:question_detail', kwargs={'pk': self.pk})


class Choice(models.Model):
    question = models.ForeignKey(Question,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name='question_choice')
    choice_text = models.CharField(_('Antwortmöglichkeit'), max_length=200)
    value = models.IntegerField(_('Wert'), default=0)

    def __str__(self):
        return str(self.choice_text)


class Answer(models.Model):
    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=10)
    answer_text = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    questionnaire = models.ForeignKey('Questionnaire', on_delete=models.CASCADE, null=False, blank=False, default='')

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date)}'


class Questionnaire(models.Model):
    """Test Questionnaire"""
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE, null=True)
    is_start_questionnaire = models.BooleanField(default=False)
    is_end_questionnaire = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date)}'
