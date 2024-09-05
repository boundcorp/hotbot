import traceback
from django.db import models
from hotbot.apps.farcaster.tags import ContentTags
from hotbot.utils.models import TimestampMixin, UUIDMixin

class AccountQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active_status='active')

class AccountManager(models.Manager):
    def get_queryset(self):
        return AccountQuerySet(self.model, using=self._db)

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

    objects = AccountManager()

    class Meta:
        app_label = 'farcaster'

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
    
    def add_tags(self, tags):
        for tag in tags:
            AccountTag.objects.update_or_create(account=self, tag=tag)

class AccountTag(TimestampMixin, UUIDMixin, models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_tags')
    tag = models.CharField(max_length=255, choices=ContentTags.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'farcaster'