from hotbot.apps.farcaster.models import Cast, Account
from django.db.models import Count
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.tags import ContentTags
import os
def run(fid, limit=3):

    latest_casts_in_channel = Cast.objects.filter(channel__fid=fid).is_not_reply().order_by('-timestamp')

    for cast in latest_casts_in_channel.filter(moderation_status=None)[:int(limit)]:
        cast.automod_classify(verbose=True)
