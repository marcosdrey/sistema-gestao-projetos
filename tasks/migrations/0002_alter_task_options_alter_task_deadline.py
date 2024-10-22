# Generated by Django 5.1.2 on 2024-10-15 12:10

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['deadline', 'title']},
        ),
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2024, 10, 15), 'A data de término deve ser maior que a data atual.')]),
        ),
    ]
