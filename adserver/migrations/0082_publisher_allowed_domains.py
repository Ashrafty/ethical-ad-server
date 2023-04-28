# Generated by Django 3.2.18 on 2023-04-18 16:54
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('adserver', '0081_rollout_ad_prioritization_pacing'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpublisher',
            name='allowed_domains',
            field=models.CharField(blank=True, default='', help_text="A space separated list of domains where the publisher's ads can appear", max_length=1024, verbose_name='Allowed domains'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='allowed_domains',
            field=models.CharField(blank=True, default='', help_text="A space separated list of domains where the publisher's ads can appear", max_length=1024, verbose_name='Allowed domains'),
        ),
    ]
