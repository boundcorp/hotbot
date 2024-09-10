from dataclasses import dataclass
from hotbot.apps.users.models import User
from hotbot.apps.users.factories import UserFactory

import django.conf
import pytest


@pytest.fixture
def strong_pass():
    # Test password is very strong
    return "DevAuth1234!!"


@dataclass
class ProjectFixture:
    settings: django.conf.Settings
    user: User


@pytest.fixture
def project_fixture_common(db, settings):
    user = UserFactory.create()

    return ProjectFixture(settings=settings, user=user)
