import json
import os
from unittest.mock import Mock

import pytest
from google.cloud import resourcemanager_v3

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

FAKE_DEFAULT_PROJECT_ID = "example-project-default"
FAKE_PROJECTS = {
    FAKE_DEFAULT_PROJECT_ID: {},
    "example-project-enabled": {"tfc-deploy": "true"},
    "example-project-disabled": {"tfc-deploy": "false"},
    "example-project-disabled-upper": {"tfc-deploy": "FALSE"},
    "example-project-other-label": {"env": "dev"},
}


def _load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, name)) as fixture_file:
        return json.load(fixture_file)


@pytest.fixture(scope="session")
def load_fixture():
    """Return a loader for JSON files in tests/fixtures."""
    return _load_fixture


@pytest.fixture(scope="session")
def fake_default_project_id() -> str:
    return FAKE_DEFAULT_PROJECT_ID


class FakeProjectsClient:
    """Stands in for resourcemanager_v3.ProjectsClient using FAKE_PROJECTS."""

    def __init__(self, credentials=None):
        self.credentials = credentials

    def get_project(self, request):
        project_id = request.name.removeprefix("projects/")
        if project_id not in FAKE_PROJECTS:
            raise RuntimeError(f"project not found: {project_id}")
        return resourcemanager_v3.Project(
            name=request.name,
            project_id=project_id,
            labels=FAKE_PROJECTS[project_id],
            etag="fake-etag",
        )


@pytest.fixture
def mock_gcp(monkeypatch):
    """Patch Google auth and Resource Manager so no GCP credentials are needed."""
    auth_default = Mock(return_value=(Mock(), FAKE_DEFAULT_PROJECT_ID))
    monkeypatch.setattr("google.auth.default", auth_default)
    monkeypatch.setattr(
        "google.cloud.resourcemanager_v3.ProjectsClient", FakeProjectsClient
    )
    return auth_default
