# Generated by Django 4.0.3 on 2022-06-20 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0014_alter_pair_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnairestart',
            name='gender',
            field=models.CharField(choices=[('male', 'Männlich'), ('female', 'Weiblich'), ('other', 'Divers')], default='Null', max_length=6, null=True, verbose_name='Geschlecht'),
        ),
    ]
