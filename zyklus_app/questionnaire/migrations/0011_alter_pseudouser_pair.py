# Generated by Django 4.0.3 on 2022-06-17 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0010_alter_pair_ident_alter_pseudouser_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pseudouser',
            name='pair',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Paar', to='questionnaire.pair'),
        ),
    ]
