def run(channel, date="*"):
    from hotbot.apps.farcaster.utils import load_channel_from_files

    load_channel_from_files(channel, date)
