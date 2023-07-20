resource "google_workflows_workflow" "runtask-budgets" {
  name            = "runtask-budgets-${random_string.suffix.id}"
  region          = var.region
  description     = "TFC Run Task Budgets Workflow"
  service_account = google_service_account.workflow_runtasks.email
  source_contents = templatefile("${path.module}/files/workflow.yaml",
    {
      "callback_url" = google_cloudfunctions2_function.runtask_callback.url
      "process_url"  = google_cloudfunctions2_function.runtask_process.url
    }
  )
}

resource "google_project_iam_member" "workflows_invoker" {
  member  = "serviceAccount:${google_service_account.cloud_function_runtasks.email}"
  project = var.project_id
  role    = "roles/workflows.invoker"
}
