import json

import pytest
import requests_mock
from unittest.mock import Mock
from runtask_callback import main


def test_callback_handler_validate_request():
    data = {"task": {}, "result": {}}
    main.validate_request(data)
    assert main.validate_request(data) == (True, None)


def test_validate_request_blank():
    data = {}
    main.validate_request(data)
    assert main.validate_request(data) == (False, "Task detail missing in request")


def test_validate_request_task():
    data = {"task": ""}
    main.validate_request(data)
    assert main.validate_request(data) == (False, "Result detail missing in request")


def test_validate_request_result():
    data = {"result": ""}
    main.validate_request(data)
    assert main.validate_request(data) == (False, "Task detail missing in request")


def test_patch_invalid():
    url = None
    headers = None
    status = None

    with pytest.raises(TypeError):
        with requests_mock.Mocker() as mock_request:
            mock_request.patch("http://localhost:8081", text="OK", status_code=200)
            _ = main.patch(url, headers, status)


def test_patch_valid():
    url = "http://localhost:8091"
    headers = {
        "Authorization": "Bearer 12345",
        "Content-type": "application/vnd.api+json",
    }
    status = "passed"
    message = "Tests passed"

    with requests_mock.Mocker() as mock_request:
        mock_request.patch("http://localhost:8091", text="OK", status_code=200)
        response = main.patch(url, headers, status, message)

    assert response == 200


def test_callback_handler_no_data():
    data = {}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert main.callback_handler(req) == ("Payload missing in request", 422)


CALLBACK_URL = "https://app.terraform.io/api/v2/task-results/example/callback"


def _callback_request() -> Mock:
    payload = {
        "task": {
            "task_result_callback_url": CALLBACK_URL,
            "access_token": "example-token",
        },
        "result": {"status": "passed", "message": "TFC deployments enabled"},
    }
    return Mock(get_json=Mock(return_value=payload))


def test_callback_handler_valid():
    with requests_mock.Mocker() as mock_request:
        mock_request.patch(CALLBACK_URL, text="OK", status_code=200)
        assert main.callback_handler(_callback_request()) == ("OK", 200)

    sent = mock_request.request_history[0]
    assert sent.headers["Authorization"] == "Bearer example-token"
    assert sent.headers["Content-type"] == "application/vnd.api+json"
    assert json.loads(sent.body) == {
        "data": {
            "type": "task-results",
            "attributes": {"status": "passed", "message": "TFC deployments enabled"},
        }
    }


@pytest.mark.parametrize("status_code", [401, 404, 500])
def test_callback_handler_tfc_error(status_code):
    with requests_mock.Mocker() as mock_request:
        mock_request.patch(CALLBACK_URL, text="error", status_code=status_code)
        assert main.callback_handler(_callback_request()) == (
            "Internal Run Task Callback error occurred",
            500,
        )


def test_patch_http_error():
    with requests_mock.Mocker() as mock_request:
        mock_request.patch(CALLBACK_URL, text="error", status_code=500)
        with pytest.raises(main.requests.exceptions.HTTPError):
            main.patch(CALLBACK_URL, {"Authorization": "Bearer x"}, "failed", "msg")


def test_callback_handler_exception():
    req = Mock(get_json=Mock(side_effect=RuntimeError("boom")))
    assert main.callback_handler(req) == (
        "Internal Run Task Callback error occurred",
        500,
    )


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"result": {}}, "Task detail missing in request"),
        ({"task": {}}, "Result detail missing in request"),
    ],
)
def test_callback_handler_invalid_request(payload, message):
    req = Mock(get_json=Mock(return_value=payload))
    assert main.callback_handler(req) == (message, 422)
