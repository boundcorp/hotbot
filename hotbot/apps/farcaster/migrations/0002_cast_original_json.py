# Generated by Django 5.1 on 2024-09-02 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farcaster', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cast',
            name='original_json',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
