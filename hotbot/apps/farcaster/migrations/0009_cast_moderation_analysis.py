# Generated by Django 5.1.1 on 2024-09-06 21:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("farcaster", "0008_channel_description_channel_moderation_rules_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cast",
            name="moderation_analysis",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
