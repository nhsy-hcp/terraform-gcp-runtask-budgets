import json
import pytest
import os

from runtask_process import terraformplan

TERRAFORM_BASE = f"{os.path.dirname(__file__)}/../terraform"
TF_PLAN = f"{os.path.dirname(__file__)}/../runtask_process/tests/tfplan.json"

@pytest.fixture(scope="session")
def plan_json() -> str:
    with open(TF_PLAN) as plan_json_file:
        plan_json = json.load(plan_json_file)
    return plan_json

def test_get_project_ids(plan_json):
    project_ids = terraformplan.get_project_ids(plan_json)
    assert len(project_ids) > 0

def test_validate_plan(plan_json):
    result, msg = terraformplan.validate_plan(plan_json)
    assert type(result) == bool
    assert type(msg) == str