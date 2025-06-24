import google.auth
from google.cloud import resourcemanager_v3


class GoogleProject:

    def __init__(self, quota_project_id=None, scopes=None):
        self.project = None
        self.quota_project_id = quota_project_id

        if scopes == None:
            self.scopes = [
                "https://www.googleapis.com/auth/cloudplatformprojects.readonly"
            ]
        else:
            self.scopes = scopes

        credentials, default_project_id = google.auth.default(
            quota_project_id=self.quota_project_id, scopes=self.scopes
        )
        self.default_project_id = default_project_id
        self.client = resourcemanager_v3.ProjectsClient(credentials=credentials)

    def get(
        self, project_id: str
    ) -> google.cloud.resourcemanager_v3.types.projects.Project:
        """
        Retrieves a project by its ID.

        Args:
            project_id (str): The ID of the project.

        Returns:
            google.cloud.resourcemanager_v3.types.projects.Project: The project object.
        """
        request = resourcemanager_v3.GetProjectRequest(
            name="projects/{}".format(project_id)
        )
        self.project = self.client.get_project(request=request)

        return self.project

    def label(self, label: str) -> str:
        """
        Returns the value associated with the given label if it exists in the project's labels.

        Parameters:
            label (str): The label to search for.

        Returns:
            str: The value associated with the label, or an empty string if the label does not exist.
        """
        value = ""

        if self.project and label:
            if "labels" in self.project:
                if label.lower() in self.project.labels:
                    value = self.project.labels[label.lower()]

        return value


if __name__ == "__main__":
    proj = GoogleProject()
    proj.get(proj.default_project_id)
    print(proj.project)
