# -*- coding: utf-8 -*-
import traceback
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from hotbot.apps.farcaster.webhooks import (
    automod_webhook_curate,
    automod_webhook_exclude,
    neynar_webhook_receiver,
)
from hotbot.utils.admin import admin_site
from hotbot.utils.views import healthz

# Unused
api_router = DefaultRouter(trailing_slash=True)
api_router.include_root_view = settings.DEBUG
api_router.include_format_suffixes = False

urlpatterns = [
    path("api/", include(api_router.urls)),
    path("mgmt/", admin_site.urls),
    path("healthz/", healthz),
    path("api/neynar-webhook/", neynar_webhook_receiver),
    path("api/automod-webhook-curate/<str:channel_id>/", automod_webhook_curate),
    path("api/automod-webhook-exclude/<str:channel_id>/", automod_webhook_exclude),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
