from fastapi import Depends
from mountaineer import RenderBase
from django_mountaineer.controllers import SyncControllerBase
from hotbot.utils.auth import AuthDependencies, UserProfileOutput
import inspect
import os


class HomeRender(RenderBase):
    user: UserProfileOutput | None


class PageController(SyncControllerBase):
    def __init__(self, url: str | None = None, page_path="src/pages"):
        self.url = url or self.get_page_path(page_path)
        self.view_path = f"{self.get_controller_path()}/page.tsx"

    def get_page_path(self, page_path: str) -> str:
        abs_path = os.path.abspath(
            (inspect.stack()[1])[1]
        )  # get the path of the file that called this function
        parts = abs_path.split("/")
        views_index = parts.index(
            "views"
        )  # find the first 'views' folder in the hierarchy
        controller_path = "/".join(parts[views_index + 1 : -1])
        url = controller_path.split(page_path)[1] or "/"
        if url.endswith("/index"):
            url = url[:-5]
        return url

    def get_controller_path(self) -> str:
        abs_path = os.path.abspath(
            (inspect.stack()[1])[1]
        )  # get the path of the file that called this function
        parts = abs_path.split("/")
        views_index = parts.index(
            "views"
        )  # find the first 'views' folder in the hierarchy
        return "/".join(parts[views_index + 1 : -1])


# Need to wrap render in sync_to_async
class HomeController(PageController):
    def __init__(self):
        super().__init__()

    def render(
        self, user: UserProfileOutput | None = Depends(AuthDependencies.get_user)
    ) -> HomeRender:
        return HomeRender(user=user)
