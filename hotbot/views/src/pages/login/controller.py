from django.contrib.auth import alogin
from fastapi import Depends
from mountaineer import Metadata, RenderBase, sideeffect, APIException
from pydantic import BaseModel
from starlette.requests import Request
from asgiref.sync import sync_to_async
from django_mountaineer.controllers import PageController
from hotbot.utils.auth import AuthDependencies, UserProfileOutput


class FormError(APIException):
    status_code: int = 400
    detail: str = "An error occurred while processing the form"
    field_errors: dict[str, str] | None = None


class LoginRender(RenderBase):
    user: UserProfileOutput | None = None


class LoginForm(BaseModel):
    username: str
    password: str


class LoginController(PageController):
    def render(
        self,
        user: UserProfileOutput | None = Depends(AuthDependencies.get_user),
    ) -> LoginRender:
        return LoginRender(
            user=user and UserProfileOutput.from_django(user),
            metadata=Metadata(title="login"),
        )

    @sideeffect
    async def login(self, form: LoginForm, request: Request) -> None:
        if not form.username or not form.password:
            raise FormError(status_code=400, detail="Invalid username or password")

        from django.contrib.auth import authenticate

        user = await sync_to_async(authenticate)(
            username=form.username, password=form.password
        )
        if not user:
            raise FormError(status_code=400, detail="Invalid username or password")
        await alogin(request.state.django_request, user)
