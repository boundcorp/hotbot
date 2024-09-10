from importlib import import_module
from typing import Type
from asgiref.sync import sync_to_async

from fastapi import Depends
from pydantic import ConfigDict
from starlette.requests import Request
from starlette.responses import Response
from django_mountaineer.auth import get_session, get_user_from_session, SessionStore
from djantic import ModelSchema
from django.contrib.auth import get_user_model

User = get_user_model()


# These are just some sensible defaults for the user model, from the cookie cutter
# You can override these in your own project
class UserProfileOutput(ModelSchema):
    model_config = ConfigDict(  # type: ignore[typeddict-unknown-key]
        model=User, include=["id", "username", "email", "first_name", "last_name"]
    )


SessionStoreType = Type[SessionStore]


class AuthDependencies:
    @staticmethod
    async def get_user(
        request: Request,
        response: Response,
        session: SessionStoreType = Depends(get_session),
    ):
        # If you have the middleware wrapper installed, django_request will be available
        if hasattr(request.state, "django_request"):
            user = await request.state.django_request.auser()
        else:
            # Otherwise, we have fastapi-alternative implementations of the django session store and user lookup
            user = await sync_to_async(get_user_from_session)(
                request, response, session
            )
        if user.is_anonymous:
            return None

        return UserProfileOutput.model_validate(user, from_attributes=True)

    @staticmethod
    async def require_user(user=Depends(get_user)):
        if user.is_anonymous:
            raise Exception("User is not authenticated")
        return user
