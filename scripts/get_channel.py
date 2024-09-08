from hotbot.apps.farcaster.api import NeynarClient

def run(channel_name_or_id):
    api = NeynarClient()
    channel = api.find_channels(channel_name_or_id)
    import json
    print(json.dumps(channel, indent=4))
