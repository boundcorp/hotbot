import os
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class NeynarClient:
    def __init__(self):
        self.api_key = os.environ.get('NEYNAR_API_KEY')
        self.base_url = 'https://api.neynar.com/v2/farcaster'
        self.base_headers = {
            'accept': 'application/json',
            'api_key': self.api_key
        }

    def _get_paginated_page(self, url, headers, limit=100, cursor=None):
        if not '?' in url:
            url += '?'
        paginated_url = f"{url}&limit={limit}"
        if cursor:
            paginated_url += f"&cursor={cursor}"
        
        logger.debug(f"Fetching {paginated_url}")
        response = requests.get(paginated_url, headers=headers)
        logger.debug(f"Response: {response.json()}")
        return response.json()

    def _get_paginated_all_results(self, url, headers, limit=100, cursor=None, result_key='results'):
        results = []
        cursor = None
        while True:
            response = self._get_paginated_page(url, headers, limit, cursor)
            results.extend(response.get(result_key, []))
            if 'next' in response:
                cursor = response['next']['cursor']
            if not cursor:
                break
        return results

    def get_cast(self, cast_hash_or_url):
        if cast_hash_or_url.startswith('https://'):
            kind = 'url'
        else:
            kind = 'hash'
        url = f"{self.base_url}/cast/?type={kind}&identifier={cast_hash_or_url}"
        response = requests.get(url, headers=self.base_headers)
        return response.json()

    def find_channels(self, channel_name_or_id):
        url = f"{self.base_url}/channel/search?q={channel_name_or_id}"
        return self._get_paginated_all_results(url, self.base_headers, result_key='channels')

    def get_cast_conversation(self, cast_hash_or_url):
        url = f"{self.base_url}/cast/conversation?identifier={cast_hash_or_url}&type=hash&reply_depth=3&include_chronological_parent_casts=true&limit=20"
        return self._get_paginated_page(url, self.base_headers)

client = NeynarClient()

