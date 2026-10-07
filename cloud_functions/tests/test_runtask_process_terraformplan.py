import pytest

from runtask_process import terraformplan


@pytest.fixture(scope="session")
def plan_json(load_fixture) -> dict:
    return load_fixture("tfplan.json")


@pytest.fixture(scope="session")
def plan_destroy_json(load_fixture) -> dict:
    return load_fixture("tfplan-destroy.json")


@pytest.fixture(scope="session")
def plan_noop_json(load_fixture) -> dict:
    return load_fixture("tfplan-noop.json")


def test_get_project_ids(plan_json):
    project_ids = terraformplan.get_project_ids(plan_json)
    assert project_ids == [
        "example-project-var",
        "example-project-one",
        "example-project-two",
    ]


def test_get_project_ids_missing_variable(plan_json):
    plan = {**plan_json, "variables": {}}
    assert "" in terraformplan.get_project_ids(plan)


def test_get_project_ids_no_google_providers():
    plan = {"configuration": {"provider_config": {"archive": {"name": "archive"}}}}
    assert terraformplan.get_project_ids(plan) == []


def test_validate_plan(plan_json):
    result, message = terraformplan.validate_plan(plan_json)
    assert result is False
    assert message == "read: 1, create: 3, delete: 1"


def test_validate_plan_destroy(plan_destroy_json):
    result, message = terraformplan.validate_plan(plan_destroy_json)
    assert result is True
    assert message == "delete: 2"


def test_validate_plan_noop(plan_noop_json):
    assert terraformplan.validate_plan(plan_noop_json) == (True, "noop")


@pytest.mark.parametrize(
    "actions, expected",
    [
        ([["no-op"], ["no-op"]], (True, "noop")),
        ([["no-op"], ["delete"]], (True, "delete: 1")),
        ([["no-op"], ["create"]], (False, "create: 1")),
        ([["update"]], (False, "update: 1")),
    ],
)
def test_validate_plan_noop_actions(actions, expected):
    plan = {"resource_changes": [{"change": {"actions": a}} for a in actions]}
    assert terraformplan.validate_plan(plan) == expected
