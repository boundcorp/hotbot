import json
from hotbot.apps.farcaster.webhooks import automod_webhook_exclude

def run(fid='hotbot'):
    with open('fixtures/automod-test.json') as f:
        data = json.load(f)

        # Simulate a POST to the automod_webhook_exclude endpoint
        from django.test import RequestFactory

        request_factory = RequestFactory()
        request = request_factory.post(f'/automod_webhook_exclude/{fid}/', data, content_type='application/json')

        response = automod_webhook_exclude(request, fid)
        print(response.status_code, response.content)
