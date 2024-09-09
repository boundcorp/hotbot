import time
from hotbot.apps.farcaster.models import Cast, Account
from django.db.models import Count
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.tags import ContentTags
import os
def run(fid, limit=3):

    latest_casts_in_channel = Cast.objects.filter(channel__fid=fid).is_not_reply().order_by('-timestamp')

    for cast in latest_casts_in_channel[:int(limit)]:
        refetch = [embed for embed in (cast.embeds or []) if 'https://x.com/' in embed.get('url', '')
                    and not cast.embed_descriptions.get(embed.get('url'))
                    or 'ERROR' in cast.embed_descriptions.get(embed.get('url'), '')
                   ]
        if refetch:
            print(f"Refetching {len(refetch)} tweets for cast {cast.hash}")
            cast.fetch_embed_descriptions(reset=True, allow_refetch=True)
            cast.automod_classify(verbose=True)
            time.sleep(120)
        else:
            print(f"No tweets to refetch for cast {cast.hash}")
