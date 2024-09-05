import traceback
from django.db import models
from hotbot.utils.models import TimestampMixin, UUIDMixin
from .account import Account
from .channel import Channel

class Cast(TimestampMixin, UUIDMixin, models.Model):
    hash = models.CharField(max_length=255, unique=True)
    thread_hash = models.CharField(max_length=255)
    parent_hash = models.CharField(max_length=255, null=True, blank=True)
    parent_url = models.URLField(null=True, blank=True)
    root_parent_url = models.URLField(null=True, blank=True)
    parent_author = models.JSONField(null=True, blank=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    timestamp = models.DateTimeField()
    embeds = models.JSONField()
    reactions = models.JSONField()
    replies = models.JSONField()
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True)
    original_json = models.JSONField(null=True, blank=True)
    conversation = models.JSONField(null=True, blank=True)

    class Meta:
        app_label = 'farcaster'

    @classmethod
    def create_from_json(cls, data):
        update_data = {
                'thread_hash': data['thread_hash'],
                'parent_hash': data['parent_hash'],
                'parent_url': data['parent_url'],
                'root_parent_url': data['root_parent_url'],
                'parent_author': data['parent_author'],
                'text': data['text'],
                'timestamp': data['timestamp'],
                'embeds': data['embeds'],
                'reactions': data['reactions'],
                'replies': data['replies'],
                'original_json': data,
        }
 
        if data['author'] and data['author']['object'] == 'user':
            author = Account.create_from_json(data['author'])
            update_data['author'] = author
        if data['channel'] and data['channel']['object'] == 'channel_dehydrated':
            channel = Channel.create_from_json(data['channel'])
            update_data['channel'] = channel
        try:
            cast, created = cls.objects.update_or_create(
                hash=data['hash'],
                defaults=update_data,
            )
        except Exception as e:
            print("Error creating cast from json", data, e)
            traceback.print_exc()
            return None
        return cast
    
    def fetch_conversation(self):
        from ..api import client
        conversation = client.get_cast_conversation(self.hash)
        self.conversation = conversation
        self.save()
        return conversation