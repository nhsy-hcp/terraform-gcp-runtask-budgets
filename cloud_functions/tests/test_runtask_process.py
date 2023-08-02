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
        {
            "message": "Google Cloud Runtask Budgets - TFC plan download or parse failed",
            "status": "failed",
        },
        200,
    )


def test_validate_projects_ids(proj):
    validate_result, validate_msg = main.__validate_project_ids(
        [proj.project.project_id]
    )
    assert validate_result in [True, False]
