import base64
import os
import requests


class TwitterClient:
    def __init__(self):
        self.api_key = os.environ.get("X_API_KEY")
        self.api_secret = os.environ.get("X_API_SECRET")
        self.access_token = os.environ.get("X_ACCESS_TOKEN")
        self.access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.environ.get("X_BEARER_TOKEN")

    def get_tweet_by_url(self, url):
        tweet_id = url.split("/")[-1].split("?")[0]

        return requests.get(
            f"https://api.x.com/2/tweets/{tweet_id}?tweet.fields=created_at,text,username&expansions=author_id&user.fields=username",
            headers={
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
            },
        ).json()
