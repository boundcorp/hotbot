from datetime import timedelta
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
X_DOT_COM = "https://x.com/"


class CastQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def is_reply(self):
        return self.filter(parent_hash__isnull=False).active()

    def is_not_reply(self):
        return self.filter(parent_hash__isnull=True).active()


class CastManager(models.Manager):
    def get_queryset(self):
        return CastQuerySet(self.model, using=self._db)


class ModerationStatus(models.TextChoices):
    EXCLUDED = "excluded", "Excluded"
    NO_ACTION = "no_action", "No Action"
    CURATED = "curated", "Curated"


class Cast(TimestampMixin, UUIDMixin, models.Model):
    hash = models.CharField(max_length=255, unique=True)
    thread_hash = models.CharField(max_length=255)
    parent_hash = models.CharField(max_length=255, null=True, blank=True)
    parent_url = models.URLField(null=True, blank=True)
    root_parent_url = models.URLField(null=True, blank=True)
    parent_author = models.JSONField(null=True, blank=True)
    author = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True, related_name="casts"
    )
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    embeds = models.JSONField(blank=True)
    reactions = models.JSONField(blank=True)
    replies = models.JSONField(blank=True)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, null=True, blank=True, related_name="casts"
    )
    original_json = models.JSONField(null=True, blank=True)
    conversation = models.JSONField(null=True, blank=True)
    embed_descriptions = models.JSONField(default=dict, blank=True)

    last_refetched_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    action_log = models.JSONField(default=list, blank=True)

    moderation_analysis = models.JSONField(null=True, blank=True)
    moderation_duration = models.FloatField(null=True, blank=True)
    moderation_log = models.JSONField(default=list, blank=True)
    moderation_status = models.CharField(
        max_length=255, choices=ModerationStatus.choices, null=True, blank=True
    )

    objects = CastManager()

    class ApiCastNotFound(Exception):
        pass

    class Meta:
        app_label = "farcaster"
        ordering = ["-timestamp"]

    @classmethod
    def fetch_by_hash(cls, hash):
        from ..api import client

        data = client.get_cast(hash)
        if not data or data.get("code") == "NotFound":
            raise cls.ApiCastNotFound(f"Cast {hash} not found")
        try:
            return cls.create_from_json(data["cast"])
        except Exception as e:
            logger.error("Error creating cast from json", data, e)
            traceback.print_exc()
            return None

    @classmethod
    def create_from_json(cls, data, channel=None):
        update_data = {
            "thread_hash": data["thread_hash"],
            "parent_hash": data["parent_hash"],
            "parent_url": data["parent_url"],
            "root_parent_url": data["root_parent_url"],
            "parent_author": data["parent_author"],
            "text": data["text"],
            "timestamp": data["timestamp"],
            "embeds": data["embeds"],
            "reactions": data["reactions"],
            "replies": data["replies"],
            #'original_json': data,
        }

        if data["author"] and data["author"]["object"] == "user":
            author = Account.create_from_json(data["author"])
            update_data["author"] = author
        if (
            not channel
            and data["channel"]
            and data["channel"]["object"] == "channel_dehydrated"
        ):
            channel = Channel.create_from_json(data["channel"])
            update_data["channel"] = channel
        elif channel:
            update_data["channel"] = channel
        try:
            cast, created = cls.objects.update_or_create(
                hash=data["hash"],
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

    def refetch_cast(self, force=False, refetch_interval: timedelta = timedelta(days=1)):
        if not force and self.last_refetched_at and timezone.now() - self.last_refetched_at < refetch_interval:
            return self
        self.log_action(f"Re-fetching cast {self.hash} (last fetched {self.last_refetched_at})")
        try:
            Cast.fetch_by_hash(self.hash)
            self.last_refetched_at = timezone.now()
            self.save()
        except Cast.ApiCastNotFound:
            self.log_action(f"Cast {self.hash} not found")
            self.is_deleted = True
            self.save()
        except Exception as e:
            self.log_action(f"Error fetching cast {self.hash}: {e}")
            traceback.print_exc()
        self.refresh_from_db()
        return self

    def add_tags(self, tags):
        for tag in tags:
            CastTag.objects.update_or_create(cast=self, tag=tag)

    def log_moderation(self, message):
        logger.debug("Moderation: %s", message)
        self.moderation_log.append(
            {"message": message, "timestamp": timezone.now().isoformat()}
        )
        self.save()
    
    def log_action(self, message):
        logger.info("Cast Action: %s", message)
        self.action_log.append(
            {"message": message, "timestamp": timezone.now().isoformat()}
        )
        self.save()

    def short_summary(self, max_length=300, include_embeds=False, include_engagement=False):
        summary = f"=> Cast {self.hash} by {self.author.username} (ID {self.author.fid}, AKA {self.author.display_name}) on {self.timestamp}: {self.short_text_summary(max_length)}"
        if include_embeds and self.embed_descriptions:
            summary += f"\n\nEmbeds: {json.dumps(self.embed_descriptions, indent=2)}"
        if include_engagement:
            summary += f"\n\nEngagement: {self.reactions.get('likes_count', 0)} likes, {self.replies.get('count', 0)} replies"
        return summary

    def short_text_summary(self, max_length=300):
        content = self.text.replace("\n", " ")
        return f"{content[:max_length]}{'...' if len(content) > max_length else ''}"

    def fetch_embed_tweet_description(self, embed):
        from ..twitter import TwitterClient

        if embed["url"] in self.embed_descriptions:
            return True
        self.log_moderation(f"Fetching tweet {embed['url']}")
        tweet = None
        try:
            tweet = TwitterClient().get_tweet_by_url(embed["url"])
            self.embed_descriptions[embed["url"]] = (
                f"TWEET by {tweet['data']['username']}: {tweet['data']['text']}"
            )
            self.save()
            return True
        except Exception as e:
            self.log_moderation(f"Error fetching tweet {embed['url']}: {tweet} - {e}")
            traceback.print_exc()
            self.embed_descriptions[embed["url"]] = "ERROR: Failed to fetch tweet"
            self.save()
            return False

    def fetch_embed_cast_description(self, embed):
        if embed["cast_id"]["hash"] in self.embed_descriptions:
            return True
        try:
            embedded_cast = Cast.objects.get(hash=embed["cast_id"]["hash"])
            self.log_moderation(f"Found embed cast {embed['cast_id']['hash']}")
        except Cast.DoesNotExist:
            self.log_moderation(f"Fetching embed cast {embed['cast_id']['hash']}")
            try:
                embedded_cast = Cast.fetch_by_hash(embed["cast_id"]["hash"])
            except Cast.ApiCastNotFound:
                self.log_moderation(f"Embed cast {embed['cast_id']['hash']} not found")
                self.embed_descriptions[embed["cast_id"]["hash"]] = (
                    "ERROR: Embedded cast not found"
                )
                self.save()
                return False
        if (
            embedded_cast
            and embedded_cast.embeds
            and not embedded_cast.embed_descriptions
        ):
            embedded_cast.fetch_embed_descriptions(allow_refetch=False)
            embedded_cast.refresh_from_db()
        self.embed_descriptions[embed["cast_id"]["hash"]] = embedded_cast.short_summary(
            max_length=200, include_embeds=True
        )
        self.save()
        return True

    def fetch_embed_image_description(self, embed):
        from hotbot.apps.farcaster.analysis.image_description import ImageDescription

        if embed["url"] in self.embed_descriptions:
            return
        self.log_moderation(f"Parsing embed image {embed['url']}")
        try:
            result = ImageDescription.describe_image(self, embed["url"])
            self.embed_descriptions[embed["url"]] = "IMAGE: " + result.description
        except Exception as e:
            self.log_moderation(f"Error parsing embed image {embed['url']}: {e}")
            traceback.print_exc()
            self.embed_descriptions[embed["url"]] = "ERROR: Failed to parse image"
        self.save()

    def fetch_embed_url_description(self, embed):
        if embed["url"] in self.embed_descriptions:
            return True
        if X_DOT_COM in embed["url"]:
            return self.fetch_embed_tweet_description(embed)
        if "image" in embed["metadata"]:
            return self.fetch_embed_image_description(embed)
        elif "html" in embed["metadata"]:
            if "ogTitle" in embed["metadata"]["html"]:
                self.embed_descriptions[embed["url"]] = (
                    embed["metadata"]["html"]["ogTitle"]
                    + " "
                    + embed["metadata"]["html"].get("ogDescription", "")
                )
                self.save()
                return True
            else:
                self.log_moderation(f"Embed url {embed['url']} has no ogTitle")
        else:
            self.log_moderation(f"Unknown embed type: {json.dumps(embed, indent=2)}")

    def fetch_embed_descriptions(self, allow_refetch=True, reset=False):
        needs_retry = False
        if reset:
            self.embed_descriptions = {}
            self.save()
        for embed in self.embeds or []:
            if "cast_id" in embed:
                self.fetch_embed_cast_description(embed)
            elif "url" in embed:
                status = embed.get("metadata", {}).get("_status", "PENDING")
                if status == "PENDING" and not X_DOT_COM in embed["url"]:
                    if allow_refetch:
                        self.refetch_cast()
                        needs_retry = True
                    self.log_moderation(f"Skipping pending embed {embed['url']}")
                else:
                    self.fetch_embed_url_description(embed)
            else:
                self.log_moderation(
                    f"Unknown embed type: {json.dumps(embed, indent=2)}"
                )
                self.embed_descriptions[embed["url"]] = "ERROR: Unknown embed type"
                self.save()
        if needs_retry and allow_refetch:
            self.log_moderation("Refetch cast to update PENDING url embeds...")
            time.sleep(1)
            self.refresh_from_db()
            self.fetch_embed_descriptions(allow_refetch=False)

    def moderation_classify(self, verbose=False):
        import time

        start_time = time.time()
        self.moderation_log = []
        self.fetch_embed_descriptions()
        analysis = self.perform_moderation_analysis(verbose=verbose)
        self.moderation_duration = time.time() - start_time
        self.save()
        if verbose:
            print(f"Classified in {self.moderation_duration:.2f} seconds")
        self.log_action(f"Classified in {self.moderation_duration:.2f} seconds")
        return analysis

    def perform_moderation_analysis(self, verbose=False):
        from ..analysis import ModerationAnalysis

        system_prompt = ModerationAnalysis.build_system_prompt(self.channel)
        user_prompt = ModerationAnalysis.build_user_prompt(self)
        analysis = ModerationAnalysis.parse_content(
            user_prompt, system_prompt=system_prompt
        )
        self.moderation_analysis = analysis.model_dump()
        self.cast_tags.all().delete()
        self.add_tags(analysis.tags)
        self.moderation_status = (
            analysis.should_exclude
            and ModerationStatus.EXCLUDED
            or ModerationStatus.NO_ACTION
        )
        self.save()
        if verbose:
            print()
            print("---")
            print(self.short_summary(800, include_embeds=True))
            print(analysis.model_dump_json(indent=2))
            print("---")
        return analysis


class CastTag(TimestampMixin, UUIDMixin, models.Model):
    cast = models.ForeignKey(Cast, on_delete=models.CASCADE, related_name="cast_tags")
    tag = models.CharField(max_length=255, choices=ContentTags.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "farcaster"
