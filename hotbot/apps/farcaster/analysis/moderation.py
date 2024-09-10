from pydantic import Field
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.models.cast import Cast
from hotbot.apps.farcaster.models.channel import Channel
from hotbot.apps.farcaster.tags import ContentTags
from django.db.models import Count


class ModerationAnalysis(GenerativeModel):
    analysis: str = Field(description="A summary of the analysis, up to 75 characters")
    tags: list[str] = Field(description="A list of tags to apply to the cast, as many as are relevant; if the cast has no other tags, it is probably original content")
    should_exclude: bool = Field(description="The final judgement: should the cast be excluded from the main feed (denied) or not (allowed)")

    @classmethod
    def build_system_prompt(cls, channel: Channel):
        TAG_CHOICES = '\n'.join(f'({tag}: {description})' for tag, description in ContentTags.choices)
        return f"""
        YOUR TASK:
        You are a spam analysis and moderation bot. You analyze a cast into a Channel and determine if it should be excluded.
        We are analyzing a cast from the Farcaster network. You will be given the target cast, the user's profile, and the channel's moderation rules.
        You will need to analyze the cast and determine if it should be excluded from the channel.
        Be especially mindful of the channel's description and moderation rules.
        For example, if the channel topic is Politics and the cast is about a political issue or user's views, this is probably on-topic.
        
        EMBEDS:
        A cast may be followed by embeds (embedded links or media, or another cast, with our best effort to extract a description).
        We should consider the embeds in our analysis; for example, if the embed is a tweet that is on-topic, the cast is probably on-topic as well.
        If there's an image or video attached, we've tried to describe it, but we may have missed some details or failed to parse it - in that case, consider the user's history.

        CONSIDER THE USER:
        If you aren't sure about this cast, consider their track record.
        Users who frequently post original content are more likely to post original content, users who frequently spam are likely to post spam, etc.
        Also notice the user's following/follower count - real users often have >50 followers (but not always, some valid users might be new).
        Users who follow many more accounts than they have followers are more likely bots and not posting original content.
        Users with >1000 followers are more likely to be real users.

        GENERAL GUIDELINES:
        Unless otherwise specified in the rules: DO exclude spam, hate speech, sexual, and unrelated promotions; DO NOT exclude off-topic.
        Channel rules supersede all other instructions, always listen to the rules.

        --- CHANNEL INFO ---
        Channel Description:
        {channel.description}
        Channel Rules:
        {channel.moderation_rules}
        --- AVAILABLE TAGS ---
        Valid tags are: (tag: description)
        {TAG_CHOICES}
        """

    @classmethod
    def build_user_prompt(cls, cast: Cast):
        other_casts = Cast.objects.filter(author__fid=cast.author.fid).exclude(hash=cast.hash).order_by('-timestamp')
        other_tags = other_casts.values('cast_tags__tag').annotate(tag_count=Count('cast_tags__tag')).order_by('-tag_count')

        return f"""
        --- Target Cast ---
        {cast.short_summary(800, include_embeds=True)}

        --- User Track Record ---
        {other_casts.count()} casts
        {', '.join(f'{tag["cast_tags__tag"]}: {tag["tag_count"]}' for tag in other_tags if tag["tag_count"] >= 1 and tag["cast_tags__tag"])}

        --- User Details ---
        {cast.author.follower_count} followers
        {cast.author.following_count} following
        {cast.author.bio}
        """