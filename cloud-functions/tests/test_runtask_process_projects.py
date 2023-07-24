import pytest
from runtask_process import google_project


@pytest.fixture
def proj() -> google_project.GoogleProject:
    proj = google_project.GoogleProject()
    proj.get(proj.default_project_id)

    return proj


def test_project(proj):
    assert proj.project.project_id == proj.default_project_id
    assert "etag" in proj.project

def test_project_label_invalid(proj):
    assert proj.label("1234567890") == ""


def test_project_label_missing(proj):
    with pytest.raises(TypeError):
        assert proj.label()
