from hotbot.apps.farcaster.models import Cast, Account
from django.db.models import Count
from hotbot.apps.agents.services import GenerativeModel
from hotbot.apps.farcaster.tags import ContentTags
import os
def run(fid, limit=3):

    latest_casts_in_channel = Cast.objects.filter(channel__fid=fid).is_not_reply().order_by('-timestamp')[:int(limit)]

    os.unlink(f"analysis-{fid}.txt")

    for cast in latest_casts_in_channel:
        analysis = cast.automod_classify(verbose=True)
        with open(f"analysis-{fid}.txt", "a") as f:
            f.write(f"------\n{cast.short_summary(800, include_embeds=True)}\n{analysis.model_dump_json(indent=2)}\n\n")
