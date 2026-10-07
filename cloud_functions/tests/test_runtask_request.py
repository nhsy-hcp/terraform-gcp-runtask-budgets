import hashlib
import hmac
import json
import pytest
import os
import sys

sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_request")


from unittest.mock import Mock
from runtask_request import main


@pytest.fixture(scope="session")
def test_request():
    headers = {
        "x-tfc-task-signature": "b7832ce69b791e39105e50ca55039aede4778caec8e24a20c2f6acaa5274e397cef80a450b44acd6fcc62517784ae970021c338314301c5f39e7ae579db29249"
    }

    payload = {
        "plan_json_api_url": "https://localhost:8080/api/v1/plan",
        "organization_name": "00000",
        "stage": "test",
        "workspace_name": "00000",
    }

    return {"headers": headers, "payload": payload}


def test__validate_request(test_request):
    result, message = main.__validate_request(
        test_request["headers"], test_request["payload"]
    )
    assert message == "OK"
    assert result


def test_validate_hmac(test_request):
    key = "secret"
    result = main.__validate_hmac(
        key,
        json.dumps(test_request["payload"]).encode("utf-8"),
        test_request["headers"]["x-tfc-task-signature"],
    )
    assert result


def test_request_handler_missing():
    data = {}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert main.request_handler(req) == ("Payload missing in request", 200)


def _signed_request(payload: dict, key: str = "secret") -> Mock:
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(key.encode("utf-8"), body, hashlib.sha512).hexdigest()
    return Mock(
        get_json=Mock(return_value=payload),
        get_data=Mock(return_value=body),
        headers={"x-tfc-task-signature": signature},
    )


@pytest.fixture
def mock_workflows(monkeypatch):
    """Replace the Workflows clients so no GCP calls are made."""
    executions = Mock()
    executions.return_value.create_execution.return_value = Mock(name="execution")
    workflows = Mock()
    workflows.return_value.workflow_path.return_value = (
        "projects/p/locations/l/workflows/w"
    )
    monkeypatch.setattr(main.executions_v1, "ExecutionsClient", executions)
    monkeypatch.setattr(main.workflows_v1, "WorkflowsClient", workflows)
    return executions


def test_request_handler_valid(test_request, mock_workflows):
    req = _signed_request(test_request["payload"])
    assert main.request_handler(req) == ("OK", 200)

    create = mock_workflows.return_value.create_execution
    create.assert_called_once()
    execution = create.call_args.kwargs["execution"]
    assert json.loads(execution.argument) == test_request["payload"]


def test_request_handler_workflow_error(test_request, mock_workflows):
    mock_workflows.return_value.create_execution.side_effect = RuntimeError("boom")
    req = _signed_request(test_request["payload"])
    assert main.request_handler(req) == ("Workflow execution error", 500)


def test_request_handler_hmac_invalid(test_request, mock_workflows):
    req = _signed_request(test_request["payload"], key="wrong-key")
    assert main.request_handler(req) == ("HMAC signature invalid", 422)
    mock_workflows.return_value.create_execution.assert_not_called()


@pytest.mark.parametrize(
    "setting, message",
    [
        ("HMAC_KEY", "HMAC key environment variable missing on server"),
        ("RUNTASK_PROJECT", "Project environment variable missing on server"),
        ("RUNTASK_REGION", "Region environment variable missing on server"),
        ("RUNTASK_WORKFLOW", "Workflow name environment variable missing on server"),
    ],
)
def test_request_handler_missing_config(monkeypatch, test_request, setting, message):
    monkeypatch.setattr(main, setting, False)
    req = _signed_request(test_request["payload"])
    assert main.request_handler(req) == (message, 500)


def test_request_handler_exception():
    req = Mock(get_json=Mock(side_effect=RuntimeError("boom")))
    assert main.request_handler(req) == (
        "Internal Run Task Request error occurred",
        500,
    )


@pytest.mark.parametrize(
    "headers, payload_update, message",
    [
        (None, {}, "Headers missing in request"),
        ({}, {}, "TFC Task signature missing"),
        (
            "signed",
            {"organization_name": None},
            "TFC payload missing : organization_name",
        ),
        ("signed", {"stage": None}, "TFC payload missing : stage"),
        ("signed", {"workspace_name": None}, "TFC payload missing : workspace_name"),
        (
            "signed",
            {"plan_json_api_url": None},
            "TFC payload missing : plan_json_api_url",
        ),
        (
            "signed",
            {"stage": "pre_plan"},
            "TFC Runtask stage verification failed: pre_plan",
        ),
    ],
)
def test__validate_request_invalid(test_request, headers, payload_update, message):
    if headers == "signed":
        headers = test_request["headers"]
    payload = dict(test_request["payload"])
    for key, value in payload_update.items():
        if value is None:
            payload.pop(key)
        else:
            payload[key] = value
    assert main.__validate_request(headers, payload) == (False, message)


def test__validate_request_payload_none(test_request):
    assert main.__validate_request(test_request["headers"], None) == (
        False,
        "Payload missing in request",
    )


@pytest.mark.parametrize(
    "tfc_org, workspace_prefix, expected",
    [
        ("00000", False, (True, "OK")),
        ("other-org", False, (False, "TFC Org verification failed : 00000")),
        (False, "000", (True, "OK")),
        (
            False,
            "prod-",
            (False, "TFC workspace prefix verification failed : 00000"),
        ),
    ],
)
def test__validate_request_filters(
    monkeypatch, test_request, tfc_org, workspace_prefix, expected
):
    monkeypatch.setattr(main, "TFC_ORG", tfc_org)
    monkeypatch.setattr(main, "WORKSPACE_PREFIX", workspace_prefix)
    result = main.__validate_request(test_request["headers"], test_request["payload"])
    assert result == expected


def test_request_handler_invalid_request(test_request, mock_workflows):
    payload = {k: v for k, v in test_request["payload"].items() if k != "stage"}
    req = _signed_request(payload)
    assert main.request_handler(req) == ("TFC payload missing : stage", 422)
    mock_workflows.return_value.create_execution.assert_not_called()
