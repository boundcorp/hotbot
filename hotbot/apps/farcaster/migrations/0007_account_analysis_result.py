# Generated by Django 5.1.1 on 2024-09-05 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farcaster', '0006_alter_account_options_alter_cast_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='analysis_result',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
    ]
