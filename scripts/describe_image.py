from hotbot.apps.farcaster.analysis.image_description import ImageDescription
from hotbot.apps.farcaster.models import Cast
import json


def run():
    cast = Cast.objects.get(hash="0x1d00d9c8add3fda326cd479f28cba8486b3fe1e3")
    result = ImageDescription.parse_content(cast, cast.embeds[0]["url"])
    print(json.dumps(result.model_dump(), indent=2))
