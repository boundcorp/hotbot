import json
import time
import traceback
from django.db import models
from hotbot.apps.farcaster.tags import ContentTags
from hotbot.utils.models import TimestampMixin, UUIDMixin
from .account import Account
from .channel import Channel
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class CastQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active_status='active')
    
    def is_reply(self):
        return self.filter(parent_hash__isnull=False)
    
    def is_not_reply(self):
        return self.filter(parent_hash__isnull=True)

class CastManager(models.Manager):
    def get_queryset(self):
        return CastQuerySet(self.model, using=self._db)

class ModerationStatus(models.TextChoices):
    EXCLUDED = 'excluded', 'Excluded'
    NO_ACTION = 'no_action', 'No Action'
    CURATED = 'curated', 'Curated'

class Cast(TimestampMixin, UUIDMixin, models.Model):
    hash = models.CharField(max_length=255, unique=True)
    thread_hash = models.CharField(max_length=255)
    parent_hash = models.CharField(max_length=255, null=True, blank=True)
    parent_url = models.URLField(null=True, blank=True)
    root_parent_url = models.URLField(null=True, blank=True)
    parent_author = models.JSONField(null=True, blank=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='casts')
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    embeds = models.JSONField(blank=True)
    reactions = models.JSONField(blank=True)
    replies = models.JSONField(blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True, related_name='casts')
    original_json = models.JSONField(null=True, blank=True)
    conversation = models.JSONField(null=True, blank=True)
    embed_descriptions = models.JSONField(default=dict, blank=True)

    moderation_analysis = models.JSONField(null=True, blank=True)
    moderation_duration = models.FloatField(null=True, blank=True)
    moderation_log = models.JSONField(default=list, blank=True)
    moderation_status = models.CharField(max_length=255, choices=ModerationStatus.choices, null=True, blank=True)

    objects = CastManager()

    class Meta:
        app_label = 'farcaster'
        ordering = ['-timestamp']

    @classmethod
    def fetch_by_hash(cls, hash):
        from ..api import client
        cast = client.get_cast(hash)
        return cls.create_from_json(cast['cast'])
    
    @classmethod
    def create_from_json(cls, data, channel=None):
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
        if not channel and data['channel'] and data['channel']['object'] == 'channel_dehydrated':
            channel = Channel.create_from_json(data['channel'])
            update_data['channel'] = channel
        elif channel:
            update_data['channel'] = channel
        try:
            cast, created = cls.objects.update_or_create(
                hash=data['hash'],
                defaults=update_data,
            )
        except Exception as e:
            logger.error("Error creating cast from json", data, e)
            traceback.print_exc()
            return None
        return cast
    
    def fetch_conversation(self):
        from ..api import client
        conversation = client.get_cast_conversation(self.hash)
        self.conversation = conversation
        self.save()
        return conversation

    def add_tags(self, tags):
        for tag in tags:
            CastTag.objects.update_or_create(cast=self, tag=tag)
    
    def log_moderation(self, message):
        logger.debug("Moderation: %s", message)
        self.moderation_log.append({"message": message, "timestamp": timezone.now().isoformat()})
        self.save()

    def short_summary(self, max_length=300, include_embeds=False):
        summary = f"=> Cast {self.hash} by {self.author.username} (ID {self.author.fid}, AKA {self.author.display_name}) on {self.timestamp}: {self.short_text_summary(max_length)}"
        if include_embeds and self.embed_descriptions:
            summary += f"\n\nEmbeds: {json.dumps(self.embed_descriptions, indent=2)}"
        return summary
    
    def short_text_summary(self, max_length=300):
        content = self.text.replace("\n", " ")
        return f"{content[:max_length]}{'...' if len(content) > max_length else ''}"

    def fetch_relevant_metadata(self, allow_refetch=True):
        from hotbot.apps.farcaster.analysis.image_description import ImageDescription
        needs_refetch = False
        if self.embeds:
            for embed in self.embeds:
                if 'cast_id' in embed and embed['cast_id']['hash'] not in self.embed_descriptions:
                    try:
                        cast = Cast.objects.get(hash=embed['cast_id']['hash'])
                        self.log_moderation(f"Found embed cast {embed['cast_id']['hash']}")
                    except Cast.DoesNotExist:
                        self.log_moderation(f"Fetching embed cast {embed['cast_id']['hash']}")
                        cast = Cast.fetch_by_hash(embed['cast_id']['hash'])
                    cast.fetch_relevant_metadata(allow_refetch=False)
                    cast.refresh_from_db()
                    self.embed_descriptions[embed['cast_id']['hash']] = cast.short_summary(max_length=200, include_embeds=True)
                    self.save()
                elif 'url' in embed:
                    status = embed['metadata'].get('_status', 'PENDING')
                    if status == 'PENDING':
                        self.log_moderation("Re-fetching cast to update PENDING url embed")
                        try:
                            cast = Cast.fetch_by_hash(self.hash)
                        except Exception as e:
                            self.log_moderation(f"Error fetching cast {self.hash}: {e}")
                            traceback.print_exc()
                        self.refresh_from_db()
                        needs_refetch = True
                        break
                    else:
                        if 'image' in embed['metadata']:
                            if embed['url'] not in self.embed_descriptions:
                                self.log_moderation(f"Parsing embed image {embed['url']}")
                                try:
                                    result = ImageDescription.parse_content(self, embed['url'])
                                    self.embed_descriptions[embed['url']] = result.description
                                except Exception as e:
                                    self.log_moderation(f"Error parsing embed image {embed['url']}: {e}")
                                    traceback.print_exc()
                                    self.embed_descriptions[embed['url']] = "Failed to parse image"
                                self.save()
                        elif 'html' in embed['metadata']:
                            if 'ogTitle' in embed['metadata']['html']:
                                self.embed_descriptions[embed['url']] = (
                                    embed['metadata']['html']['ogTitle'] + " " +
                                    embed['metadata']['html'].get('ogDescription', '')
                                )
                        else:
                            self.log_moderation(f"Embed url {embed['url']} is {status}")
                            print(json.dumps(embed, indent=2))
                else:
                    print(json.dumps(embed, indent=2))
        if needs_refetch and allow_refetch:
            self.log_moderation("Needs refetch, fetching again...")
            time.sleep(1)
            self.fetch_relevant_metadata(allow_refetch=False)


    def automod_classify(self, verbose=False):
        import time
        start_time = time.time()
        self.moderation_log = []
        self.fetch_relevant_metadata()
        analysis = self.perform_moderation_analysis(verbose=verbose)
        self.moderation_duration = time.time() - start_time
        self.save()
        if verbose:
            print(f"Classified in {self.moderation_duration:.2f} seconds")
        return analysis
    
    def perform_moderation_analysis(self, verbose=False):
        from ..analysis import ModerationAnalysis
        system_prompt = ModerationAnalysis.build_system_prompt(self.channel)
        user_prompt = ModerationAnalysis.build_user_prompt(self)
        analysis = ModerationAnalysis.parse_content(user_prompt, system_prompt=system_prompt)
        self.moderation_analysis = analysis.model_dump()
        self.cast_tags.all().delete()
        self.add_tags(analysis.tags)
        self.moderation_status = analysis.should_exclude and ModerationStatus.EXCLUDED or ModerationStatus.NO_ACTION
        self.save()
        if verbose:
            print()
            print("---")
            print(self.short_summary(800, include_embeds=True))
            print(analysis.model_dump_json(indent=2))
            print("---")
        return analysis

class CastTag(TimestampMixin, UUIDMixin, models.Model):
    cast = models.ForeignKey(Cast, on_delete=models.CASCADE, related_name='cast_tags')
    tag = models.CharField(max_length=255, choices=ContentTags.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'farcaster'