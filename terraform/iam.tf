resource "google_service_account" "cloud_function_runtasks" {
  account_id = "cloud-function-runtasks"
}

resource "google_service_account" "cloud_function_runtask_process" {
  account_id = "cloud-function-runtask-process"
}

resource "google_service_account" "workflow_runtasks" {
  account_id = "workflow-runtasks"
}

# Allow runtask_process cloud function to lookup project labels
resource "google_project_iam_member" "project_viewer" {
  for_each = toset(var.project_viewer)
  member   = "serviceAccount:${google_service_account.cloud_function_runtask_process.email}"
  project  = each.value
  role     = "roles/browser"
}
