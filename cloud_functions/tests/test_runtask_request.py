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
        "x-tfc-task-signature": "5545ca49fbcee7cd22bb3b2ba2268389a5666c52fa70f13678d8ab0163f29899d0ec3e94d73cc124bfc92e6b47ed6ef2ba6f099b7ed010b288224e7063044bb9"
    }

    payload = {
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
