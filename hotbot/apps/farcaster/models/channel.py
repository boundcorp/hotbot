import traceback
from django.db import models
from hotbot.utils.models import TimestampMixin, UUIDMixin


class Channel(TimestampMixin, UUIDMixin, models.Model):
    fid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=2048, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    moderation_enabled = models.BooleanField(default=False)
    moderation_rules = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "farcaster"

    @classmethod
    def create_from_json(cls, data):
        try:
            channel, created = cls.objects.update_or_create(
                fid=data["id"],
                defaults={
                    "name": data["name"],
                    "image_url": data["image_url"],
                },
            )
        except Exception as e:
            print("Error creating channel from json", data, e)
            traceback.print_exc()
            return None
        return channel

    def __str__(self):
        return self.name
