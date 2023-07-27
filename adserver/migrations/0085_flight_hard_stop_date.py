# Generated by Django 3.2.20 on 2023-07-25 23:46
import datetime

from django.db import migrations
from django.db import models

import adserver.models


class Migration(migrations.Migration):

    dependencies = [
        ('adserver', '0084_publisher_traffic_shaping'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='hard_stop',
            field=models.BooleanField(default=False, help_text='The flight will be stopped on the end date even if not completely fulfilled', verbose_name='Hard stop'),
        ),
        migrations.AddField(
            model_name='historicalflight',
            name='hard_stop',
            field=models.BooleanField(default=False, help_text='The flight will be stopped on the end date even if not completely fulfilled', verbose_name='Hard stop'),
        ),
        migrations.AlterField(
            model_name='flight',
            name='end_date',
            field=models.DateField(default=adserver.models.default_flight_end_date, help_text='The estimated end date for the flight', verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='flight',
            name='start_date',
            field=models.DateField(db_index=True, default=datetime.date.today, help_text='This flight will not be shown before this date', verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='historicalflight',
            name='end_date',
            field=models.DateField(default=adserver.models.default_flight_end_date, help_text='The estimated end date for the flight', verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='historicalflight',
            name='start_date',
            field=models.DateField(db_index=True, default=datetime.date.today, help_text='This flight will not be shown before this date', verbose_name='Start Date'),
        ),
    ]
