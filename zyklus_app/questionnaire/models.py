import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# Create your models here.
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

        if not user_code:
            raise ValueError(_('Sie müssen Ihren User-Code eingeben'))

        user = self.model(user_code=user_code, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Pair(models.Model):
    """Forms a pair of persons"""
    ident = models.CharField(max_length=10)

    def __str__(self):
        return self.ident


class QuestionnaireStart(models.Model):
    """Lookup Questionnaire"""
    question_one = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_two = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_three = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)],
                                                      default=0)
    question_four = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_five = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_six = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)

    date = datetime.datetime.now()


class QuestionnaireEnd(models.Model):
    """Completion Questionnaire"""
    question_one = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_two = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_three = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)],
                                                      default=0)
    question_four = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_five = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_six = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    date = datetime.datetime.now()


class PseudoUser(AbstractBaseUser, PermissionsMixin):
    user_code = models.CharField(_('Persönlicher Code'), max_length=10, unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, null=True)
    questionnaire_start = models.OneToOneField(QuestionnaireStart, on_delete=models.CASCADE, null=True)
    questionnaire_end = models.OneToOneField(QuestionnaireEnd, on_delete=models.CASCADE, null=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'user_code'

    def __str__(self):
        return self.user_code


class QuestionnaireDaily(models.Model):
    """Daily Questionnaire"""
    question_one = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_two = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_three = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)],
                                                      default=0)
    question_four = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_five = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    question_six = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)], default=0)
    date = datetime.datetime.now()

    pseudo_user = models.ForeignKey(PseudoUser, on_delete=models.CASCADE, null=True)
