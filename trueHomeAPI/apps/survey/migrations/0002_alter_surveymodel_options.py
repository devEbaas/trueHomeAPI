# Generated by Django 4.0.1 on 2022-01-10 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='surveymodel',
            options={'verbose_name': 'Survey', 'verbose_name_plural': 'Surveys'},
        ),
    ]