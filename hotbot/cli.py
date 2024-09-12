from click import option, group
from mountaineer.cli import handle_runserver, handle_watch, handle_build
#import django
import os


#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotbot.settings")
#django.setup()


@group()
def cli():
    pass


@cli.command()
@option("--port", default=5006, help="Port to run the server on")
@option("--host", default="127.0.0.1", help="Host to run the server on")
@option("--live-reload-port", default=5007, help="Port to run the live reload server on")
def runserver(port: int, host: str, live_reload_port: int):
    handle_runserver(
        package="hotbot",
        webservice="hotbot.app:app_controller.app",
        webcontroller="hotbot.app:app_controller",
        port=port,
        #host=host,
        #live_reload_port=live_reload_port,
    )


@cli.command()
def watch():
    handle_watch(
        package="hotbot",
        webcontroller="hotbot.app:app_controller",
    )


@cli.command()
def build():
    handle_build(
        webcontroller="hotbot.app:app_controller",
    )


if __name__ == "__main__":
    cli()
