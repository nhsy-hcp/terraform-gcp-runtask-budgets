resource "google_project_service" "apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "workflows.googleapis.com"
  ])

  service                    = each.value
  disable_on_destroy         = false
  disable_dependent_services = false
}