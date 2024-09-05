import traceback
from django.db import models
from hotbot.utils.models import TimestampMixin, UUIDMixin

class Account(TimestampMixin, UUIDMixin, models.Model):
    fid = models.IntegerField(unique=True)
    custody_address = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    display_name = models.CharField(max_length=1024, null=True, blank=True)
    pfp_url = models.URLField(max_length=2048, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    follower_count = models.PositiveIntegerField(null=True, blank=True)
    following_count = models.PositiveIntegerField(null=True, blank=True)
    verifications = models.JSONField(null=True, blank=True)
    primary_address = models.CharField(max_length=255, null=True, blank=True)
    verified_addresses = models.JSONField(null=True, blank=True)
    active_status = models.CharField(max_length=50, null=True, blank=True)
    power_badge = models.BooleanField(null=True, blank=True)
    farcaster_created_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create_from_json(cls, data):
        verified_addresses = data['verified_addresses']
        if verified_addresses and verified_addresses.get('eth_addresses'):
            primary_address = verified_addresses['eth_addresses'][0]
        else:
            primary_address = None
        if data['active_status'] == 'inactive' and data['username'] == f"!{data['fid']}":
            print("Skipping inactive user", data['username'], data.get('display_name'))
            return None
        try:
            account, created = cls.objects.update_or_create(
                fid=data['fid'],
                defaults={
                    'custody_address': data['custody_address'],
                    'username': data['username'],
                    'display_name': data['display_name'],
                    'pfp_url': data['pfp_url'],
                    'bio': data['profile']['bio']['text'],
                    'follower_count': data['follower_count'],
                    'following_count': data['following_count'],
                    'verifications': data['verifications'],
                    'verified_addresses': data['verified_addresses'],
                    'active_status': data['active_status'],
                    'power_badge': data['power_badge'],
                    'primary_address': primary_address,
                }
            )
        except Exception as e:
            print("Error creating account from json", data, e)
            traceback.print_exc()
            return None
        return account

    def __str__(self):
        return f"{self.display_name} ({self.username} #{self.fid})"

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
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, null=True, blank=True)
    original_json = models.JSONField(null=True, blank=True)
    conversation = models.JSONField(null=True, blank=True)

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
        from .api import client
        conversation = client.get_cast_conversation(self.hash)
        self.conversation = conversation
        self.save()
        return conversation

class Channel(TimestampMixin, UUIDMixin, models.Model):
    fid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=2048, null=True, blank=True)

    @classmethod
    def create_from_json(cls, data):
        try:
            channel, created = cls.objects.update_or_create(
                fid=data['id'],
            defaults={
                'name': data['name'],
                'image_url': data['image_url'],
                }
            )
        except Exception as e:
            print("Error creating channel from json", data, e)
            traceback.print_exc()
            return None
        return channel
    
    def __str__(self):
        return self.name