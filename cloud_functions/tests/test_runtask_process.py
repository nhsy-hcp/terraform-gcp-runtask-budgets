import os
import sys

sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_process")

from unittest.mock import Mock
import pytest
from runtask_process import main
from runtask_process import googleproject


@pytest.fixture(scope="session")
def proj() -> googleproject.GoogleProject:
    proj = googleproject.GoogleProject()
    proj.get(proj.default_project_id)

    return proj


def test_process_handler():
    data = {
        "access_token": "00000",
        "plan_json_api_url": "00000",
    }
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert main.process_handler(req) == (
        {"message": "TFC plan download failed", "status": "failed"},
        200,
    )


def test_process_handler_missing_payload():
    data = {}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert main.process_handler(req) == (
        {"message": "Payload missing in request", "status": "failed"},
        422,
    )


@pytest.mark.gcp
def test_validate_projects_ids(proj):
    validate_result, validate_message = main.__validate_project_ids(
        [proj.project.project_id]
    )
    assert validate_result in [True, False]


@pytest.mark.parametrize(
    "project_ids, expected",
    [
        (
            ["example-project-enabled", "example-project-other-label"],
            (
                True,
                "TFC deployments enabled: "
                "example-project-enabled, example-project-other-label",
            ),
        ),
        (
            ["example-project-enabled", "example-project-disabled"],
            (False, "TFC deployments disabled: example-project-disabled"),
        ),
        (
            ["example-project-disabled-upper"],
            (False, "TFC deployments disabled: example-project-disabled-upper"),
        ),
        (
            ["example-project-unknown"],
            (False, "Google project label lookup failed: example-project-unknown"),
        ),
    ],
)
def test_validate_projects_ids_mocked(mock_gcp, project_ids, expected):
    assert main.__validate_project_ids(project_ids) == expected
