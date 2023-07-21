from google.cloud import resourcemanager_v3
import google.auth


class Project:

    def __init__(self, quota_project_id=None):
        self.quota_project_id = quota_project_id

        self.scopes = [
            "https://www.googleapis.com/auth/cloudplatformprojects.readonly"
        ]

        credentials, project = google.auth.default(quota_project_id=self.quota_project_id, default_scopes=self.scopes)
        self.default_project_id = project
        self.client = resourcemanager_v3.ProjectsClient(credentials=credentials)

    def get(self, project_id: str) -> google.cloud.resourcemanager_v3.types.projects.Project:
        request = resourcemanager_v3.GetProjectRequest(name="projects/{}".format(project_id))
        response = self.client.get_project(request=request)

        return response

if __name__ == "__main__":
    client = Project()
    project = client.get(client.default_project_id)
    print(project)
