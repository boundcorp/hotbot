from fastapi import Depends
from mountaineer import RenderBase

from django_mountaineer.controllers import PageController
from hotbot.utils.auth import AuthDependencies, UserProfileOutput



class HomeRender(RenderBase):
    user: UserProfileOutput | None

# Need to wrap render in sync_to_async
class HomeController(PageController()):
    def render( self, user: UserProfileOutput | None = Depends(AuthDependencies.get_user) ) -> HomeRender:
        return HomeRender(
            user=user
        )