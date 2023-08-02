import json
import pytest
import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_request")


import requests_mock
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
    result, msg = main.__validate_request(test_request["headers"], test_request["payload"])
    assert msg == "OK"
    assert result == True


def test_validate_hmac(test_request):
    key = "secret"
    result = main.__validate_hmac(key, json.dumps(test_request["payload"]).encode("utf-8"), test_request["headers"]["x-tfc-task-signature"])
    assert result == True


def test_request_handler_missing():
    data = {}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert main.request_handler(req) == ('Payload missing in request', 200)


def test_request_handler_valid(test_request):
    req = Mock(
            get_json=Mock(return_value=test_request["payload"]),
            get_data=Mock(return_value=json.dumps(test_request["payload"]).encode("utf-8")),
            headers=test_request["headers"],
            args=test_request["payload"].keys())
    assert main.request_handler(req) == ('Workflow execution error', 500)
