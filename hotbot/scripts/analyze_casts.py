from hotbot.apps.farcaster.models import Cast, Account
from django.db.models import Count
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.tags import ContentTags

class ContentAnalysis(GenerativeModel):
    analysis: str
    tags: list[str]

    @classmethod
    def system_prompt(cls):
        TAG_CHOICES = '\n'.join(f'({tag}: {description})' for tag, description in ContentTags.choices)
        return f"""
        You are an expert at analyzing content. You analyze the content of a cast and determine which of the tags are appropriate.
        We are analyzing a cast from the Farcaster network. You will be given multiple casts from an account, including the parent cast if relevant.
        ---
        Valid tags are: (tag: description)
        {TAG_CHOICES}
        """


def run(fid):
    accounts_by_cast_count = (
        Account.objects
        .filter(analysis_result__isnull=True)
        .filter(casts__channel__fid=fid)
        .annotate(cast_count=Count('casts'))
        .order_by('-cast_count')
    )

    for account in accounts_by_cast_count[:8]:
        print(account.display_name, account.cast_count)
        casts = Cast.objects.filter(author=account, channel__fid=fid)
        cast_summaries = '\n'.join(cast.short_summary() for cast in casts)

        user_prompt = f"""
        {account.display_name} has posted the following {casts.count()} casts:
        {cast_summaries}
        """

        analysis = ContentAnalysis.parse_content(user_prompt)
        print(f"Analyzed {account.display_name} ({casts.count()} casts): {analysis}")
        print(f"Tags: {analysis.tags}")
        print()

        account.analysis_result = analysis.analysis
        account.account_tags.all().delete()
        account.add_tags(analysis.tags)
        account.save()
