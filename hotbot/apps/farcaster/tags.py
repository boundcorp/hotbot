from django.db.models import TextChoices


class ContentTags(TextChoices):
    AUTOMATED = 'automated', 'Automated'
    USER_GIVING_TIPS_WITH_CONTENT = 'user_giving_tips_with_content', 'User Giving Tips, post also contains original content'
    USER_GIVING_TIPS_WITHOUT_CONTENT = 'user_giving_tips_without_content', 'User Giving Tips, no original content'
    BOT_TIP_REPLY = 'bot_tip_reply', 'Bot Tip Reply, automated reply to a tipping message, usually saying remaining balance'
    ORIGINAL_CONTENT = 'original_content', 'Original Content, a real human message, it is on-topic and valid user content (as opposed to spam, nonsense, or tipping-without-content), its not just "haha" or "great point"'
    SPAM = 'spam', 'Spam'
    OFF_TOPIC = 'off_topic', 'Off Topic'
    HATE_SPEECH = 'hate_speech', 'Hate Speech'
    SEXUALLY_EXPLICIT = 'sexually_explicit', 'Sexually Explicit'
