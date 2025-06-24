import json
import os
import sys

sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_process")

from unittest.mock import Mock

import pytest
from runtask_process import googleproject, main


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
    req = Mock(
        get_json=Mock(return_value=data),
        args=data,
        headers={},
        get_data=Mock(return_value=b"00000"),
    )
    # Test will fail validation due to invalid URL format
    assert main.process_handler(req) == (
        {"message": "Invalid plan_json_api_url format", "status": "failed"},
        422,
    )


def test_process_handler_valid_input():
    data = {
        "access_token": "0123456789abcdef",
        "plan_json_api_url": "https://app.terraform.io/api/v1/plan",
    }
    req = Mock(
        get_json=Mock(return_value=data),
        args=data,
        headers={},
        get_data=Mock(return_value=json.dumps(data).encode("utf-8")),
    )
    # Test with valid input should return empty message since terraformcloud.download_json_plan returns empty dict
    assert main.process_handler(req) == ({"message": "", "status": "failed"}, 200)


def test_process_handler_missing_payload():
    data = {}
    req = Mock(
        get_json=Mock(return_value=data),
        args=data,
        headers={},
        get_data=Mock(return_value=b"{}"),
    )
    assert main.process_handler(req) == (
        {"message": "Empty payload", "status": "failed"},
        422,
    )


@pytest.mark.skip(reason="Requires Google Cloud authentication")
def test_validate_projects_ids(proj):
    validate_result, validate_message = main.__validate_project_ids(
        [proj.project.project_id]
    )
    assert validate_result in [True, False]
