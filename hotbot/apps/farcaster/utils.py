import glob
import json
from hotbot.apps.farcaster.models import Account, Channel, Cast


def load_channel_from_files(channel_id, date="*"):
    PATTERN = f"fixtures/casts/{channel_id}-{date}.json"
    files = glob.glob(PATTERN)
    for file in files:
        with open(file, "r") as f:
            for line in f:
                data = json.loads(line)
                cast = Cast.create_from_json(data["data"])
