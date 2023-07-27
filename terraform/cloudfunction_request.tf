data "archive_file" "runtask_request" {
  type        = "zip"
  source_dir  = "../cloud_functions/runtask_request"
  output_path = "../build/runtask_request.zip"

  excludes = ["__pycache__", "testing", "Makefile"]
}

resource "google_storage_bucket_object" "runtask_request" {
  name   = "runtask_request_${random_string.suffix.id}_${data.archive_file.runtask_request.output_md5}.zip"
  bucket = google_storage_bucket.cloud_functions.name
  source = data.archive_file.runtask_request.output_path
}

resource "google_cloudfunctions2_function" "runtask_request" {
  name        = "runtask-request-${random_string.suffix.id}"
  description = "runtask-request handler"
  location    = var.region

  build_config {
    runtime     = "python310"
    entry_point = "request_handler"
    source {
      storage_source {
        bucket = google_storage_bucket.cloud_functions.name
        object = google_storage_bucket_object.runtask_request.name
      }
    }
  }

  service_config {
    available_cpu    = "1"
    available_memory = "128Mi"
    environment_variables = {
      HMAC_KEY         = var.hmac_key
      RUNTASK_PROJECT  = var.project_id
      RUNTASK_REGION   = var.region
      RUNTASK_WORKFLOW = google_workflows_workflow.runtask-budgets.name
    }
    ingress_settings                 = "ALLOW_ALL"
    max_instance_count               = 1
    max_instance_request_concurrency = 3
    service_account_email            = google_service_account.cloud_function_runtasks.email
    timeout_seconds                  = 30
  }
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions2_function_iam_member" "runtask_request_invoker" {
  project        = google_cloudfunctions2_function.runtask_request.project
  location       = google_cloudfunctions2_function.runtask_request.location
  cloud_function = google_cloudfunctions2_function.runtask_request.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

resource "google_cloud_run_service_iam_member" "runtask_request_cloud_run_invoker" {
  project  = google_cloudfunctions2_function.runtask_request.project
  location = google_cloudfunctions2_function.runtask_request.location
  service  = google_cloudfunctions2_function.runtask_request.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

check "cloudfunction_request_health" {
  data "http" "cloudfunction_request" {
    url = google_cloudfunctions2_function.runtask_request.url
  }
  assert {
    condition     = data.http.cloudfunction_request.status_code == 200
    error_message = format("Cloud function request unhealthy: %s - %s", data.http.cloudfunction_request.status_code, data.http.cloudfunction_request.response_body)
  }
}
