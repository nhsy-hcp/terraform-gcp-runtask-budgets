import pytest
from runtask_process import projects


@pytest.fixture
def client() -> projects.Project:
    client = projects.Project()
    return client


def test_project(client):
    project_id = client.default_project_id
    project = client.get(project_id)

    assert project.project_id == project_id
    assert "etag" in project
