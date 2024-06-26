# Generated by Django 4.2.11 on 2024-03-26 21:57
import django.db.models.deletion
import django_extensions.db.fields
import jsonfield.fields
from django.conf import settings
from django.db import migrations
from django.db import models

import adserver.analyzer.validators

class Migration(migrations.Migration):

    replaces = [
        ("adserver_analyzer", "0001_initial"),
        ("adserver_analyzer", "0002_last_ad_served_to_datefield"),
        ("adserver_analyzer", "0003_add_embeddings"),
        ("adserver_analyzer", "0004_add_embeddings"),
        ("adserver_analyzer", "0005_add_analyzedad"),
        ("adserver_analyzer", "0006_remove_embedding"),
    ]

    initial = True

    dependencies = [
        ("adserver", "0067_add_adimpression_viewtime"),
        ("adserver", "0093_publisher_ignore_mobile_traffic"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AnalyzedUrl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        db_index=True,
                        help_text="URL of the page being analyzed after certain query parameters are stripped away",
                        max_length=1024,
                    ),
                ),
                (
                    "keywords",
                    jsonfield.fields.JSONField(
                        blank=True,
                        null=True,
                        validators=[adserver.analyzer.validators.KeywordsValidator()],
                        verbose_name="Keywords for this URL",
                    ),
                ),
                (
                    "last_analyzed_date",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        default=None,
                        help_text="Last time the ad server analyzed this URL",
                        null=True,
                    ),
                ),
                (
                    "last_ad_served_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        help_text="Last date an ad was served for this URL",
                        null=True,
                    ),
                ),
                (
                    "visits_since_last_analyzed",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of times ads have been served for this URL since it was last analyzed",
                    ),
                ),
                (
                    "publisher",
                    models.ForeignKey(
                        help_text="Publisher where this URL appears",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="adserver.publisher",
                    ),
                ),
            ],
            options={
                "unique_together": {("url", "publisher")},
            },
        ),
        migrations.CreateModel(
            name="AnalyzedAdvertiserUrl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        db_index=True,
                        help_text="URL of the page being analyzed after certain query parameters are stripped away",
                        max_length=1024,
                    ),
                ),
                (
                    "keywords",
                    jsonfield.fields.JSONField(
                        blank=True,
                        null=True,
                        validators=[adserver.analyzer.validators.KeywordsValidator()],
                        verbose_name="Keywords for this URL",
                    ),
                ),
                (
                    "last_analyzed_date",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        default=None,
                        help_text="Last time the ad server analyzed this URL",
                        null=True,
                    ),
                ),
                (
                    "title",
                    models.TextField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Title of the page",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Description of the page",
                    ),
                ),
                (
                    "advertiser",
                    models.ForeignKey(
                        help_text="Advertiser with the URL",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="adserver.advertiser",
                    ),
                ),
            ],
            options={
                "unique_together": {("url", "advertiser")},
            },
        ),
        migrations.AddField(
            model_name="analyzedurl",
            name="description",
            field=models.TextField(
                blank=True,
                default=None,
                null=True,
                verbose_name="Description of the page",
            ),
        ),
        migrations.AddField(
            model_name="analyzedurl",
            name="title",
            field=models.TextField(
                blank=True, default=None, null=True, verbose_name="Title of the page"
            ),
        ),
    ]
