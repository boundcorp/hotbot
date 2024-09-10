# Generated by Django 5.1 on 2024-09-02 20:18

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("fid", models.IntegerField(unique=True)),
                (
                    "custody_address",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("username", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "display_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("pfp_url", models.URLField(blank=True, null=True)),
                ("bio", models.TextField(blank=True, null=True)),
                ("follower_count", models.PositiveIntegerField(blank=True, null=True)),
                ("following_count", models.PositiveIntegerField(blank=True, null=True)),
                ("verifications", models.JSONField(blank=True, null=True)),
                (
                    "primary_address",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("verified_addresses", models.JSONField(blank=True, null=True)),
                (
                    "active_status",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("power_badge", models.BooleanField(blank=True, null=True)),
                ("farcaster_created_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ("-updated_at", "-created_at"),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Channel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("fid", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ("-updated_at", "-created_at"),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Cast",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("hash", models.CharField(max_length=255, unique=True)),
                ("thread_hash", models.CharField(max_length=255)),
                (
                    "parent_hash",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("parent_url", models.URLField(blank=True, null=True)),
                ("root_parent_url", models.URLField(blank=True, null=True)),
                ("parent_author", models.JSONField(blank=True, null=True)),
                ("text", models.TextField()),
                ("timestamp", models.DateTimeField()),
                ("embeds", models.JSONField()),
                ("reactions", models.JSONField()),
                ("replies", models.JSONField()),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="farcaster.account",
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="farcaster.channel",
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at", "-created_at"),
                "abstract": False,
            },
        ),
    ]
