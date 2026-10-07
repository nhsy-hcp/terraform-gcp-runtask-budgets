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


def _plan(project_id: str, actions: list) -> dict:
    """Minimal plan with one google provider project and the given resource actions."""
    return {
        "resource_changes": [{"change": {"actions": a}} for a in actions],
        "configuration": {
            "provider_config": {
                "google": {
                    "name": "google",
                    "expressions": {"project": {"constant_value": project_id}},
                }
            }
        },
    }


def _handle(monkeypatch, plan_json) -> tuple:
    monkeypatch.setattr(
        main.terraformcloud, "download_json_plan", Mock(return_value=plan_json)
    )
    data = {"access_token": "example-token", "plan_json_api_url": "https://example"}
    req = Mock(get_json=Mock(return_value=data))
    return main.process_handler(req)


@pytest.mark.parametrize(
    "plan_json, expected",
    [
        (
            _plan("example-project-enabled", [["create"]]),
            {
                "message": "TFC deployments enabled: example-project-enabled",
                "status": "passed",
            },
        ),
        (
            _plan("example-project-disabled", [["create"]]),
            {
                "message": "TFC deployments disabled: example-project-disabled",
                "status": "failed",
            },
        ),
        (
            _plan("example-project-disabled", [["delete"], ["delete"]]),
            {"message": "TFC deployments override: delete: 2", "status": "passed"},
        ),
        (
            _plan("example-project-disabled", [["no-op"]]),
            {"message": "TFC deployments override: noop", "status": "passed"},
        ),
    ],
)
def test_process_handler_plans(mock_gcp, monkeypatch, plan_json, expected):
    assert _handle(monkeypatch, plan_json) == (expected, 200)


def test_process_handler_destroy_fixture(mock_gcp, monkeypatch, load_fixture):
    result, code = _handle(monkeypatch, load_fixture("tfplan-destroy.json"))
    assert (result["status"], code) == ("passed", 200)


def test_process_handler_empty_plan(monkeypatch):
    assert _handle(monkeypatch, {}) == (
        {"message": "TFC plan download failed", "status": "failed"},
        200,
    )


def test_process_handler_no_google_projects(monkeypatch):
    plan_json = {"resource_changes": [{"change": {"actions": ["create"]}}]}
    assert _handle(monkeypatch, plan_json) == (
        {"message": "No Google project ids found in TFC plan", "status": "failed"},
        200,
    )


def test_process_handler_plan_parse_failed(monkeypatch):
    monkeypatch.setattr(
        main.terraformplan, "get_project_ids", Mock(side_effect=ValueError("bad"))
    )
    result = _handle(monkeypatch, _plan("example-project-enabled", [["create"]]))
    assert result == ({"message": "TFC plan parse failed", "status": "failed"}, 200)


def test_process_handler_exception():
    req = Mock(get_json=Mock(side_effect=RuntimeError("boom")))
    assert main.process_handler(req) == (
        "Internal Run Task Process error occurred",
        500,
    )
