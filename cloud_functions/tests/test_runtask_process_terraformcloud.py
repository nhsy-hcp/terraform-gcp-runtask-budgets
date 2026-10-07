import pytest
import requests
import requests_mock

from runtask_process import terraformcloud

PLAN_URL = "https://app.terraform.io/api/v2/plans/plan-example/json-output"


def test_download_json_plan(load_fixture):
    plan = load_fixture("tfplan.json")
    with requests_mock.Mocker() as mock_request:
        mock_request.get(PLAN_URL, json=plan, status_code=200)
        result = terraformcloud.download_json_plan("example-token", PLAN_URL)

    assert result == plan
    sent = mock_request.request_history[0]
    assert sent.headers["Authorization"] == "Bearer example-token"
    assert sent.headers["Content-Type"] == "application/vnd.api+json"


@pytest.mark.parametrize("status_code", [204, 401, 404, 500])
def test_download_json_plan_not_ok(status_code):
    with requests_mock.Mocker() as mock_request:
        mock_request.get(PLAN_URL, text="error", status_code=status_code)
        assert terraformcloud.download_json_plan("example-token", PLAN_URL) == {}


def test_download_json_plan_connection_error():
    with requests_mock.Mocker() as mock_request:
        mock_request.get(PLAN_URL, exc=requests.exceptions.ConnectionError)
        with pytest.raises(requests.exceptions.ConnectionError):
            terraformcloud.download_json_plan("example-token", PLAN_URL)
