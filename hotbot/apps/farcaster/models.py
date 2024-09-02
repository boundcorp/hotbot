from django.db import models
from hotbot.utils.models import TimestampMixin, UUIDMixin

class Account(TimestampMixin, UUIDMixin, models.Model):
    fid = models.IntegerField(unique=True)
    custody_address = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    pfp_url = models.URLField(null=True, blank=True)
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
        if verified_addresses and 'eth_addresses' in verified_addresses:
            primary_address = verified_addresses['eth_addresses'][0]
        else:
            primary_address = None
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
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField()
    embeds = models.JSONField()
    reactions = models.JSONField()
    replies = models.JSONField()
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def create_from_json(cls, data):
        author = Account.create_from_json(data['author'])
        channel = Channel.create_from_json(data['channel'])
        cast, created = cls.objects.update_or_create(
            hash=data['hash'],
            defaults={
                'thread_hash': data['thread_hash'],
                'parent_hash': data['parent_hash'],
                'parent_url': data['parent_url'],
                'root_parent_url': data['root_parent_url'],
                'parent_author': data['parent_author'],
                'author': author,
                'text': data['text'],
                'timestamp': data['timestamp'],
                'embeds': data['embeds'],
                'reactions': data['reactions'],
                'replies': data['replies'],
                'channel': channel,
            }
        )
        return cast

class Channel(TimestampMixin, UUIDMixin, models.Model):
    fid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    @classmethod
    def create_from_json(cls, data):
        channel, created = cls.objects.update_or_create(
            fid=data['fid'],
            defaults={
                'name': data['name'],
            }
        )
        return channel
    
    def __str__(self):
        return self.name