from pydantic import Field
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.models.cast import Cast
from hotbot.apps.farcaster.models.channel import Channel
from hotbot.apps.farcaster.tags import ContentTags
from django.db.models import Count


class ModerationAnalysis(GenerativeModel):
    analysis: str = Field(description="A summary of the analysis, up to 100 characters")
    tags: list[str] = Field(description="A list of tags to apply to the cast, as many as are relevant; if the cast has no other tags, it is probably original content")
    should_exclude: bool = Field(description="Whether the cast should be excluded from the main feed (denied)")

    @classmethod
    def build_system_prompt(cls, channel: Channel):
        TAG_CHOICES = '\n'.join(f'({tag}: {description})' for tag, description in ContentTags.choices)
        return f"""
        You are a spam analysis and moderation bot. You analyze a cast into a Channel and determine if it should be excluded.
        We are analyzing a cast from the Farcaster network. You will be given the target cast, the user's profile, and the channel's moderation rules.
        You will need to analyze the cast and determine if it should be excluded from the channel.
        Be especially mindful of the channel's description and moderation rules.
        A cast may be followed by embeds (embedded links or media, or another cast, with our best effort to extract a description), we should consider the embeds in our analysis.
        For example, if the topic is Politics and the cast is about a political issue or user's views, this is probably on-topic, unless specified by the rules.
        If you aren't sure about this cast, consider their track record. Users who frequently post original content are more likely to post original content.
        Also consider the user's following/follower count - real users often have >50 followers. Users who follow many more accounts than they have followers are likely bots and not posting original content.
        Do not exclude content just for being off-topic, unless the rules say to exclude off-topic content.
        Unless otherwise specified in the rules, exclude anything that is spam, hate speech, or sexual.
        ---
        Channel Description:
        {channel.description}
        Channel Rules:
        {channel.moderation_rules}
        ---
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