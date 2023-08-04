import json
import os
import pytest
import requests
import tftest

from requests.exceptions import HTTPError

BASE_DIR = f"{os.path.dirname(__file__)}/../terraform"

if "DISABLE_DESTROY" in os.environ and os.environ["DISABLE_DESTROY"] == "1":
    DISABLE_DESTROY = True
else:
    DISABLE_DESTROY = False


@pytest.fixture(scope="session")
def plan():
    tf = tftest.TerraformTest(tfdir=BASE_DIR)
    if not DISABLE_DESTROY:
        tf.setup(use_cache=True)

    return tf.plan(output=True, use_cache=True)


@pytest.fixture(scope="session")
def apply():
    targets = []
    # targets = [
    #     "google_storage_bucket.cloud_functions",
    #     "google_cloudfunctions2_function.runtask_process"
    # ]
    tf = tftest.TerraformTest(BASE_DIR)

    if not DISABLE_DESTROY:
        tf.setup(use_cache=True, cleanup_on_exit=True)

    tf.apply(output=True, use_cache=True, targets=targets)
    yield tf.output()

    if not DISABLE_DESTROY:
        tf.destroy(use_cache=True, **{"auto_approve": True})


@pytest.fixture(scope="session")
def state(apply):
    with open(os.path.join(BASE_DIR, "terraform.tfstate")) as state_file:
        return tftest.TerraformState(json.load(state_file))


@pytest.mark.plan
def test_variables(plan):
    tf_vars = plan.variables
    assert "project_id" in tf_vars, "project_id not in tf var plan"


@pytest.mark.plan
def test_plan_gcs_cloud_function(plan):
    res = plan.resources['google_storage_bucket.cloud_functions']
    assert 'google_storage_bucket.cloud_functions' in plan.resources
    assert res['values']['location'] == plan.variables['region'].upper()
    assert res['values']['uniform_bucket_level_access'] == True


def test_state_gcs_cloud_function(state):
    id = state.resources["None.random_string.suffix"]['instances'][0]['attributes']['id']
    gcs_id = state.resources["None.google_storage_bucket.cloud_functions"]['instances'][0]['attributes']['id']
    assert gcs_id == "runtask-cloud-functions-{}".format(id)


def test_state_cloud_function_callback(state):
    cloud_function_state = state.resources["None.google_cloudfunctions2_function.runtask_callback"]['instances'][0]['attributes']['state']
    assert cloud_function_state == "ACTIVE"


def test_state_cloud_function_process(state):
    cloud_function_state = state.resources["None.google_cloudfunctions2_function.runtask_process"]['instances'][0]['attributes']['state']
    assert cloud_function_state == "ACTIVE"


def test_state_cloud_function_request(state):
    cloud_function_state = state.resources["None.google_cloudfunctions2_function.runtask_request"]['instances'][0]['attributes']['state']
    assert cloud_function_state == "ACTIVE"


def test_apply_outputs(apply):
    assert len(apply) > 0


def test_apply_cloud_function_callback_uri(apply):
    url = apply["runtask_callback_uri"]

    with pytest.raises(HTTPError) as exc_info:
        response = requests.get(url)
        response.raise_for_status()

    assert exc_info.value.response.status_code == 403


def test_apply_cloud_function_request_uri(apply):
    url = apply["runtask_request_uri"]

    with pytest.raises(HTTPError) as exc_info:
        response = requests.get(url)
        response.raise_for_status()

    assert exc_info.value.response.status_code == 403


def test_apply_cloud_function_process_uri(apply):
    url = apply["runtask_process_uri"]

    with pytest.raises(HTTPError) as exc_info:
        response = requests.get(url)
        response.raise_for_status()

    assert exc_info.value.response.status_code == 403


def test_apply_api_gateway_uri(apply):
    url = apply["api_gateway_endpoint_uri"]

    response = requests.post(url)
    response.raise_for_status()

    assert response.status_code == 200
