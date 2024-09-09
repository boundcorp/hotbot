def run(*message):
    from hotbot.apps.farcaster.api import client
    client.post_cast(" ".join(message))