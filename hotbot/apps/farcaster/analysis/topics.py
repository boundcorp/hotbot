from pydantic import Field
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.models.cast import Cast
from hotbot.apps.farcaster.models.channel import Channel
from hotbot.apps.farcaster.tags import ContentTags
from django.db.models import Count


class TopicExtraction(GenerativeModel):
    topics: list[str] = Field(
        description="A list of popular topics in the channel, in hashtag format without the # (eg 'Hotdog', 'Pizza', 'BananaSplit')"
    )

    @classmethod
    def build_system_prompt(cls, channel: Channel):
        return f"""
        YOUR TASK:
        Extract the most popular topics in the channel. Try to account for the channel's description and rules.
        Popularity is based on frequency of casts mentioning the topic, and relative number of reactions (likes, replies, reposts)
        
        EMBEDS:
        A cast may be followed by embeds (embedded links or media, or another cast, with our best effort to extract a description).
        We should consider the embeds in our analysis, for example if an embed is about a topic, the cast is probably about that topic.

        GENERAL GUIDELINES:
        Unless otherwise specified in the rules: DO exclude spam, hate speech, sexual, and unrelated promotions; DO NOT exclude off-topic.
        Channel rules supersede all other instructions, always listen to the rules.

        --- CHANNEL INFO ---
        Channel Description:
        {channel.description}
        Channel Rules:
        {channel.moderation_rules}
        """

    @classmethod
    def build_user_prompt(cls, channel: Channel):
        pass
