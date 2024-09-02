from hotbot.apps.farcaster.api import NeynarClient

def run(cast_hash_or_url):
    api = NeynarClient()
    cast = api.get_cast(cast_hash_or_url)
    import json
    print(json.dumps(cast, indent=4))
