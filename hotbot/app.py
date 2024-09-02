from fastapi.staticfiles import StaticFiles
from mountaineer import ConfigBase
from mountaineer.app import AppController
from mountaineer.js_compiler.postcss import PostCSSBundler
from mountaineer.render import LinkAttribute, Metadata
from django.core.asgi import get_asgi_application
import django
import os
from django_mountaineer.controllers import register_controllers
from django_mountaineer.middleware import FastAPIDjangoMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotbot.settings')
django.setup()

app_controller = AppController(
    config=ConfigBase(PACKAGE="hotbot"), # type: ignore
    
    global_metadata=Metadata(
        links=[LinkAttribute(rel="stylesheet", href="/static/src_main.css")]
    ),
    custom_builders=[
        PostCSSBundler(),
    ],
    
)

django_app = get_asgi_application()

# Automatically discover .py files in the views/src directory and load controllers
register_controllers(app_controller, ['hotbot/views/src'])

if not os.path.exists("staticfiles"):
    os.makedirs("staticfiles")
app_controller.app.mount("/staticfiles", StaticFiles(directory="staticfiles"), name="static")
app_controller.app.mount("/", django_app, name="app")

from hotbot.settings.urls import urlpatterns

# Use the FastAPIDjangoMiddleware, which runs the full django middleware for every fastapi request
app_controller.app.add_middleware(FastAPIDjangoMiddleware, django_patterns=urlpatterns)
