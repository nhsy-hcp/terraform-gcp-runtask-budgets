import pytest

from runtask_process import googleproject


@pytest.fixture
def proj() -> googleproject.GoogleProject:
    proj = googleproject.GoogleProject()
    proj.get(proj.default_project_id)

    return proj


@pytest.fixture
def mock_proj(mock_gcp) -> googleproject.GoogleProject:
    return googleproject.GoogleProject()


@pytest.mark.gcp
def test_project(proj):
    assert proj.project.project_id == proj.default_project_id
    assert "etag" in proj.project


@pytest.mark.gcp
def test_project_label_invalid(proj):
    assert proj.label("1234567890") == ""


@pytest.mark.gcp
def test_project_label_missing(proj):
    with pytest.raises(TypeError):
        proj.label()


def test_mock_project_default(mock_gcp, mock_proj, fake_default_project_id):
    project = mock_proj.get(mock_proj.default_project_id)
    assert mock_proj.default_project_id == fake_default_project_id
    assert project.project_id == fake_default_project_id
    assert "etag" in project
    mock_gcp.assert_called_once_with(
        quota_project_id=None,
        scopes=["https://www.googleapis.com/auth/cloudplatformprojects.readonly"],
    )


def test_mock_project_custom_scopes(mock_gcp):
    proj = googleproject.GoogleProject(quota_project_id="quota", scopes=["scope"])
    assert proj.scopes == ["scope"]
    mock_gcp.assert_called_once_with(quota_project_id="quota", scopes=["scope"])


@pytest.mark.parametrize(
    "project_id, label, expected",
    [
        ("example-project-enabled", "tfc-deploy", "true"),
        ("example-project-disabled", "tfc-deploy", "false"),
        ("example-project-disabled", "TFC-DEPLOY", "false"),
        ("example-project-other-label", "tfc-deploy", ""),
        ("example-project-default", "tfc-deploy", ""),
    ],
)
def test_mock_project_label(mock_proj, project_id, label, expected):
    mock_proj.get(project_id)
    assert mock_proj.label(label) == expected


def test_mock_project_label_before_get(mock_proj):
    assert mock_proj.label("tfc-deploy") == ""


def test_mock_project_label_empty(mock_proj):
    mock_proj.get("example-project-enabled")
    assert mock_proj.label("") == ""


def test_mock_project_label_missing(mock_proj):
    with pytest.raises(TypeError):
        mock_proj.label()
