from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from mountaineer import Metadata, RenderBase, LayoutControllerBase, sideeffect
from django.contrib.auth import alogout


class LayoutRender(RenderBase):
    pass


class RedirectRender(RenderBase):
    pass


class LayoutController(LayoutControllerBase):
    view_path = "src/pages/layout.tsx"

    def render(self) -> LayoutRender:
        return LayoutRender(
            metadata=Metadata(title="Home"),
        )

    @sideeffect
    async def logout(self, request: Request) -> RedirectRender:
        await alogout(request.state.django_request)
        return RedirectRender(
            metadata=Metadata(explicit_response=RedirectResponse(url="/login"))
        )
