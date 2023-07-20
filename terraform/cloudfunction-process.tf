data "archive_file" "runtask_process" {
  type        = "zip"
  source_dir  = "../cloud-functions/runtask-process"
  output_path = "../build/runtask-process-${random_string.suffix.id}.zip"

  excludes = ["__pycache__", "testing", "Makefile"]
}

resource "google_storage_bucket_object" "runtask_process" {
  name   = "runtask-process-${random_string.suffix.id}-${data.archive_file.runtask_callback.output_md5}.zip"
  bucket = google_storage_bucket.cloud_functions.name
  source = data.archive_file.runtask_process.output_path
}

resource "google_cloudfunctions2_function" "runtask_process" {
  name        = "runtask-process-${random_string.suffix.id}"
  description = "runtask-process handler"
  location    = var.region

  build_config {
    runtime     = "python310"
    entry_point = "process_handler"
    source {
      storage_source {
        bucket = google_storage_bucket.cloud_functions.name
        object = google_storage_bucket_object.runtask_process.name
      }
    }
  }

  service_config {
    available_cpu                    = "1"
    available_memory                 = "128Mi"
    ingress_settings                 = "ALLOW_ALL"
    max_instance_count               = 1
    max_instance_request_concurrency = 3
    service_account_email            = google_service_account.cloud_function_runtasks.email
    timeout_seconds                  = 30
  }
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions2_function_iam_member" "runtask_process_invoker" {
  project        = google_cloudfunctions2_function.runtask_process.project
  location       = google_cloudfunctions2_function.runtask_process.location
  cloud_function = google_cloudfunctions2_function.runtask_process.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.workflow_runtasks.email}"
}

resource "google_cloud_run_service_iam_member" "runtask_process_cloud_run_invoker" {
  project  = google_cloudfunctions2_function.runtask_process.project
  location = google_cloudfunctions2_function.runtask_process.location
  service  = google_cloudfunctions2_function.runtask_process.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.workflow_runtasks.email}"
}
