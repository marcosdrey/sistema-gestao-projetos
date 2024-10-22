# Generated by Django 5.1.2 on 2024-10-09 16:29

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='deadline',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2024, 10, 9), 'A data de término deve ser maior que a data atual.')]),
        ),
    ]