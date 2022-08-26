from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

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


class QuestionnaireEnd(models.Model):
    """Completion Questionnaire"""
    question_one = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_two = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_three = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)],
                                                      default=0)
    question_four = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_five = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_six = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    pseudo_user = models.OneToOneField(PseudoUser, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date.date())}'


class QuestionnaireStart(models.Model):
    """Lookup Questionnaire"""
    gender = models.CharField(_('Geschlecht'), max_length=6, choices=choices.GENDER_CHOICES, default='Null', null=True)
    question_one = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_two = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_three = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)],
                                                      default=0)
    question_four = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_five = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_six = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)

    date = models.DateTimeField(auto_now_add=True, blank=True)
    pseudo_user = models.OneToOneField(PseudoUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date.date())}'


class QuestionnaireDaily(models.Model):
    """Daily Questionnaire"""
    question_one = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_two = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_three = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)],
                                                      default=0)
    question_four = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_five = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_six = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date)}'


# Models for editable Questions
class Question(models.Model):
    name = models.CharField(_('Identifikator'), max_length=10, default='', unique='True')
    question_text = models.CharField(_('Frage Text'), max_length=200)
    hidden = models.BooleanField(_('Frage versteckt?'), default='False')
    show_at_question = models.CharField(_('Identifikator um angezeigt zu werden'), max_length=10, default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_('Fremdschlüssel ID'))
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.question_text)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id'])
        ]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    value = models.IntegerField(default=0)

    def __str__(self):
        return str(self.choice_text)


class Answer(models.Model):
    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=10)
    answer_text = models.CharField(max_length=200)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date)}'

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id'])
        ]


class QuestionnaireTest(models.Model):
    """Test Questionnaire"""
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE, null=True)
    GenericRelation(Answer, related_query_name='answer')

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date)}'


class QuestionnaireTestStart(models.Model):
    """Test Questionnaire"""
    gender = models.CharField(_('Geschlecht'), max_length=6, choices=choices.GENDER_CHOICES, default='Null', null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.pseudo_user} {str(self.date)}'


class QuestionCatalogue(models.Model):
    which_questionnaire = models.CharField(max_length=5, choices=choices.QUESTIONNAIRE_CHOICES, default='None',
                                           unique='True')
    GenericRelation(Question, related_query_name='question')

    def __str__(self):
        return str(self.which_questionnaire)
