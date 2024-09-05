# -*- coding: utf-8 -*-
import traceback
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from hotbot.utils.admin import admin_site
from hotbot.utils.views import healthz

# Unused
api_router = DefaultRouter(trailing_slash=True)
api_router.include_root_view = settings.DEBUG
api_router.include_format_suffixes = False

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from datetime import datetime

@csrf_exempt
def webhook_receiver(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        date_str = datetime.now().strftime("%Y-%m-%d")
        channel = body_data['data']['channel']['id'].lower()
        file_path = f'./fixtures/casts/{channel}-{date_str}.json'
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'a') as f:
            json.dump(body_data, f)
            f.write('\n')
            try:
                from hotbot.apps.farcaster.models import Cast
                Cast.create_from_json(body_data['data'])
            except Exception as e:
                traceback.print_exc()
        
        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


urlpatterns = [
    path("api/", include(api_router.urls)),
    path("mgmt/", admin_site.urls),
    path("healthz/", healthz),
    path("api/neynar-webhook/", webhook_receiver),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)