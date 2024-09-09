import os
import json
from datetime import datetime
import time
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback

from hotbot.apps.farcaster.analysis.moderation import ModerationAnalysis
from hotbot.apps.farcaster.models.channel import Channel
from hotbot.apps.farcaster.models.cast import Cast

logger = logging.getLogger(__name__)



@csrf_exempt
def neynar_webhook_receiver(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        date_str = datetime.now().strftime("%Y-%m-%d")
        channel = body_data['data']['channel']['id'].lower()
        file_path = f'./fixtures/casts/{channel}-{date_str}.json'
        kind = body_data['data'].get('parent_hash', None) and 'reply' or 'cast'
        logger.debug(f"received {kind} in {channel} by {body_data['data']['author']['username']}")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'a') as f:
            json.dump(body_data, f)
            f.write('\n')
            try:
                from hotbot.apps.farcaster.models import Cast
                cast = Cast.create_from_json(body_data['data'])
                if channel in ['politics', 'cryptoleft'] and not cast.parent_hash:
                    cast.automod_classify(verbose=True)
            except Exception as e:
                traceback.print_exc()
                logger.error(f"error creating cast in {channel}: {e}")
        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def automod_classify(data: dict, channel: Channel) -> ModerationAnalysis:
    try:
        cast = Cast.create_from_json(data['cast'], channel=channel)
        return cast.automod_classify()
    except Exception as e:
        traceback.print_exc()
        logger.error(f"error automod_classify: {e}")
        return


@csrf_exempt
def automod_webhook_curate(request, channel_id):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        channel = Channel.objects.get(fid=channel_id.lower())
        #logger.info(f"checking curate for {channel_id} by {body_data['user']['username']}")

        #analysis = automod_classify(body_data, channel)
        
        return dont_trigger_rule('ignored')

def trigger_rule(message: str):
    response = JsonResponse({'message': message[:75]}, status=200)
    print(response)
    return response

def dont_trigger_rule(message: str):
    response = JsonResponse({'message': message[:75]}, status=400)
    print(response)
    return response

@csrf_exempt
def automod_webhook_exclude(request, channel_id):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        channel = Channel.objects.get(fid=channel_id.lower())

        if channel.moderation_enabled:
            logger.info(f"checking exclusion for {channel_id} by {body_data['user']['username']}")
            result = automod_classify(body_data, channel)
            if result:
                if result.should_exclude:
                    logger.info(f"excluding {channel_id} by {body_data['user']['username']}")
                    return trigger_rule(result.analysis)
                else:
                    logger.info(f"no action for {channel_id} by {body_data['user']['username']}")
                    return dont_trigger_rule(result.analysis)
        
        return dont_trigger_rule('ignored')