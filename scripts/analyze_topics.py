
from datetime import datetime, timedelta
from typing import Iterable

from pydantic import BaseModel, Field
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.models.cast import Cast
from hotbot.apps.farcaster.models.channel import Channel

HASHTAG_FORMAT = "Use hashtag format (without the #) for each topic, camelcase, no spaces or punctuation, for example: 'TopicOne', 'TopicNumberTwo', 'ThisIsThirdTopic', 'FourthBigTopicHere'."

class TopicSeen(BaseModel):
    topic: str = Field(description="The topic that is mentioned in the cast. " + HASHTAG_FORMAT)
    casts: int = Field(description="The number of casts that have mentioned this topic.")
    likes: int = Field(description="The number of likes for the topic.")
    replies: int = Field(description="The number of replies for the topic.")

class ExtractTopics(GenerativeModel):
    """
    You are an expert at analyzing topics from user messages.
    You will be given some messages and you should look for popular topics, based on the content of the messages.
    If popularity mechanics are available for a message, these should be taken into account when determining popular topics.
    For example, a topic with one message that has lots of engagement weighted above topics that have lower engagement, even if they have more messages.
    If we provide you with a list of existing topics, use these as a baseline and try to avoid creating similar duplicates.
    """

    topics: list[TopicSeen] = Field(description=f"A list of topics that are popular in the given messages.")

    @classmethod
    def from_farcaster_channel_casts(cls, channel: Channel, casts: Iterable[Cast]) -> "ExtractTopics":
        SYSTEM = f"""
        We are analyzing casts from a channel on Farcaster (a decentralized social media network in the crypto community); casts are similar to tweets, and may have embedded images, videos, links, or other casts/tweets/replies.
        ID: {channel.fid}
        Name: {channel.name}
        Description: {channel.description}

        If the channel has a specific focus, try to only create topics that are relevant to the channel.
        """

        CASTS = "\n---\n".join([cast.refetch_cast().short_summary(include_engagement=True, include_embeds=True) for cast in casts])

        return cls.parse_content(CASTS, system_prompt=cls.__doc__ + SYSTEM)

    @classmethod
    def from_farcaster_channel(cls, channel: Channel, limit: int = 300, start_time: datetime = None, end_time: datetime = None) -> "ExtractTopics":
        casts = channel.casts.all().is_not_reply()
        if start_time:
            casts = casts.filter(timestamp__gte=start_time)
        if end_time:
            casts = casts.filter(timestamp__lte=end_time)
        return cls.from_farcaster_channel_casts(channel, casts.order_by("-created_at")[:limit])

class CastHashTopic(BaseModel):
    cast_hash: str
    topics: list[str]

class CastTopics(GenerativeModel):
    """
    You are an expert at analyzing topics from user messages.
    You will be given some messages and a list of topics, you should determine which topics are mentioned in the messages.
    """
    cast_topics: list[CastHashTopic] = Field(description="A list of every cast hash and the topics that are mentioned in the cast.")

    @classmethod
    def from_farcaster_casts(cls, casts: Iterable[Cast], topics: list[str]) -> "ExtractTopics":
        CASTS = "\n--- CASTS\n".join([cast.short_summary(include_embeds=True) for cast in casts])
        TOPICS = "\n--- TOPICS\n".join([f"#{topic}" for topic in topics])
        return cls.parse_content(CASTS, system_prompt=cls.__doc__ + TOPICS)

def run(fid='politics'):
    channel = Channel.objects.get(fid=fid)
    recent = datetime.now() - timedelta(days=30)
    extracted = ExtractTopics.from_farcaster_channel(channel, start_time=recent)
    for topic in extracted.topics:
        print(topic.topic, 'casts:', topic.casts, 'likes:', topic.likes, 'replies:', topic.replies)
    casts = channel.casts.all().is_not_reply().order_by("-created_at")[:30]
    print(f"Analyzing {len(casts)} casts")

    for cast in casts:
        cast_topics = CastTopics.from_farcaster_casts([cast], extracted.topics)
        for cast_topic in cast_topics.cast_topics:
            print(cast_topic.cast_hash, cast_topic.topics)


