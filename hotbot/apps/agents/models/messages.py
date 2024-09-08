from hotbot.utils.models import TimestampMixin, UUIDMixin
from django.db import models

class Message(TimestampMixin, UUIDMixin):
    openai_id = models.CharField(max_length=128, unique=True)
    workflow = models.CharField(max_length=64, null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    success = models.BooleanField(default=True)
    content = models.JSONField()
    refusal_reason = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    model = models.CharField(max_length=64)
    completion_tokens = models.IntegerField(null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, blank=True)
