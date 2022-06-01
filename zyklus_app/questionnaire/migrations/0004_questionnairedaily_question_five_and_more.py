# Generated by Django 4.0.3 on 2022-05-21 08:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0003_questionnairestart_question_one'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnairedaily',
            name='question_five',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairedaily',
            name='question_four',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairedaily',
            name='question_one',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairedaily',
            name='question_six',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairedaily',
            name='question_three',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairedaily',
            name='question_two',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnaireend',
            name='question_five',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnaireend',
            name='question_four',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnaireend',
            name='question_one',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnaireend',
            name='question_six',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnaireend',
            name='question_three',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnaireend',
            name='question_two',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairestart',
            name='question_five',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairestart',
            name='question_four',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairestart',
            name='question_six',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairestart',
            name='question_three',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='questionnairestart',
            name='question_two',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)]),
        ),
    ]
