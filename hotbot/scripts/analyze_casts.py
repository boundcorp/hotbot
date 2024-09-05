from itertools import count
from hotbot.apps.agents.services import prompt_to_type
from hotbot.apps.farcaster.models import Cast, Account, Channel
from django.db.models import Count
from pydantic import BaseModel
from hotbot.apps.farcaster.tags import ContentTags
TAG_CHOICES = '\n'.join(f'({tag}: {description})' for tag, description in ContentTags.choices)
SYSTEM_MESSAGE = f"""
    You are an expert at analyzing content. You analyze the content of a cast and determine which of the tags are appropriate.
    We are analyzing a cast from the Farcaster network. You will be given multiple casts from an account, including the parent cast if relevant.
    ---
    Valid tags are: (tag: description)
    {TAG_CHOICES}
    """

class ContentAnalysis(BaseModel):
    analysis: str
    tags: list[str]


def run(fid):
    accounts_by_cast_count = (
        Account.objects
        .filter(casts__channel__fid=fid)
        .annotate(cast_count=Count('casts'))
        .order_by('-cast_count')
    )

    for account in accounts_by_cast_count[:1]:
        print(account.display_name, account.cast_count)
        casts = Cast.objects.filter(author=account, channel__fid=fid)
        cast_summaries = '\n'.join(cast.short_summary() for cast in casts)

        user_prompt = f"""
        {account.display_name} has posted the following {casts.count()} casts:
        {cast_summaries}
        """

        analysis = prompt_to_type(user_prompt, ContentAnalysis, system_prompt=SYSTEM_MESSAGE)
        print(analysis)

