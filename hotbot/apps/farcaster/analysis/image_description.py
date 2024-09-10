from pydantic import Field
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.models.cast import Cast
from hotbot.apps.farcaster.models.channel import Channel
from hotbot.apps.farcaster.tags import ContentTags
from django.db.models import Count


class ImageDescription(GenerativeModel):
    description: str = Field(
        description="brief description of the image, up to 300 characters"
    )

    @classmethod
    def build_system_prompt(cls, cast: Cast):
        if cast.channel:
            channel_description = cast.channel.description
            channel_rules = cast.channel.moderation_rules
        else:
            channel_description = ""
            channel_rules = ""

        return f"""
        You are an image description bot. The following image has been included in a post on a social network.
        You will be given the image and the post. You will need to describe the image. If there is legible text, you must include the text.
        For context, I am including the post and the channel details.
        Consider the post and channel details when describing the image, as it may explain what the image means, or any characters present.
        ---
        Channel: {cast.channel.fid if cast.channel else "No Channel"}
        Channel Description:
        {channel_description}
        Channel Rules:
        {channel_rules}
        ---
        --- Target Cast ---
        {cast.short_summary(800)}
        """

    @classmethod
    def describe_image(cls, cast: Cast, image_url: str):
        return cls.parse_content(
            [{"type": "image_url", "image_url": {"url": image_url}}],
            system_prompt=cls.build_system_prompt(cast),
        )
