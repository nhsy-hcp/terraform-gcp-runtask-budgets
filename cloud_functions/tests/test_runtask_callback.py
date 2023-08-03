import pytest
import requests_mock
from unittest.mock import Mock
from runtask_callback import main

def test_callback_handler_validate_request():
    data = {
        "task": {},
        "result": {}
    }
    main.validate_request(data)
    assert main.validate_request(data) == (True, None)


def test_validate_request_blank():
    data = {}
    main.validate_request(data)
    assert main.validate_request(data) == (False, 'Task detail missing in request')


def test_validate_request_task():
    data = {
        "task": ""
    }
    main.validate_request(data)
    assert main.validate_request(data) == (False, 'Result detail missing in request')


def test_validate_request_result():
    data = {
        "result": ""
    }
    main.validate_request(data)
    assert main.validate_request(data) == (False, 'Task detail missing in request')


def test_patch_invalid():
    url = None
    headers = None
    status = None

    with pytest.raises(TypeError):
        with requests_mock.Mocker() as mock_request:
            mock_request.patch("http://localhost:8081", text="OK", status_code=200)
            response = main.patch(url, headers, status)


def test_patch_valid():
    url = "http://localhost:8091"
    headers = {
        'Authorization': 'Bearer 12345',
        'Content-type': 'application/vnd.api+json',
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
    assert main.callback_handler(req) == ('Payload missing in request', 422)
