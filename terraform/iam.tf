resource "google_service_account" "cloud_function_runtasks" {
  account_id = "cf-runtasks-${random_string.suffix.id}"
}

resource "google_service_account" "cloud_function_runtask_process" {
  account_id = "cf-runtask-process-${random_string.suffix.id}"
}

resource "google_service_account" "workflow_runtasks" {
  account_id = "wf-runtasks-${random_string.suffix.id}"
}

resource "google_service_account" "apigw_runtasks" {
  account_id = "apigw-runtasks-${random_string.suffix.id}"
}

# Allow runtask_process cloud function to lookup project labels
resource "google_project_iam_member" "project_viewer" {
  member  = "serviceAccount:${google_service_account.cloud_function_runtask_process.email}"
  project = var.project_viewer
  role    = "roles/browser"
}
