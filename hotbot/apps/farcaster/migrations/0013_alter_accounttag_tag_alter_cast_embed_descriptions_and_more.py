# Generated by Django 5.1.1 on 2024-09-07 20:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("farcaster", "0012_cast_embed_descriptions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accounttag",
            name="tag",
            field=models.CharField(
                choices=[
                    ("automated", "Automated"),
                    (
                        "user_giving_tips_with_content",
                        "User Giving Tips, post also contains original content",
                    ),
                    (
                        "user_giving_tips_without_content",
                        "User Giving Tips, no original content",
                    ),
                    (
                        "bot_tip_reply",
                        "Bot Tip Reply, automated reply to a tipping message, usually saying remaining balance",
                    ),
                    (
                        "original_content",
                        'Original Content, a real human message, it is on-topic and valid user content (as opposed to spam, nonsense, or tipping-without-content), its not just "haha" or "great point"',
                    ),
                    ("spam", "Spam"),
                    (
                        "off_topic",
                        "Off Topic - completely unrelated to channel topic, very low likelihood of being relevant discussion. If unsure, dont tag as off-topic.",
                    ),
                    (
                        "hate_speech",
                        "Hate Speech - explicit racism, sexism, homophobia, transphobia, etc",
                    ),
                    ("sexually_explicit", "Sexually Explicit"),
                ],
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="cast",
            name="embed_descriptions",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="casttag",
            name="tag",
            field=models.CharField(
                choices=[
                    ("automated", "Automated"),
                    (
                        "user_giving_tips_with_content",
                        "User Giving Tips, post also contains original content",
                    ),
                    (
                        "user_giving_tips_without_content",
                        "User Giving Tips, no original content",
                    ),
                    (
                        "bot_tip_reply",
                        "Bot Tip Reply, automated reply to a tipping message, usually saying remaining balance",
                    ),
                    (
                        "original_content",
                        'Original Content, a real human message, it is on-topic and valid user content (as opposed to spam, nonsense, or tipping-without-content), its not just "haha" or "great point"',
                    ),
                    ("spam", "Spam"),
                    (
                        "off_topic",
                        "Off Topic - completely unrelated to channel topic, very low likelihood of being relevant discussion. If unsure, dont tag as off-topic.",
                    ),
                    (
                        "hate_speech",
                        "Hate Speech - explicit racism, sexism, homophobia, transphobia, etc",
                    ),
                    ("sexually_explicit", "Sexually Explicit"),
                ],
                max_length=255,
            ),
        ),
    ]
