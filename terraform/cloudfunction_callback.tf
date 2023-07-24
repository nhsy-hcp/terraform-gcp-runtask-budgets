data "archive_file" "runtask_callback" {
  type        = "zip"
  source_dir  = "../cloud_functions/runtask_callback"
  output_path = "../build/runtask-callback-${random_string.suffix.id}.zip"

  excludes = ["__pycache__", "testing", "Makefile"]
}

resource "google_storage_bucket_object" "runtask_callback" {
  name   = "runtask-callback-${random_string.suffix.id}-${data.archive_file.runtask_callback.output_md5}.zip"
  bucket = google_storage_bucket.cloud_functions.name
  source = data.archive_file.runtask_callback.output_path
}

resource "google_cloudfunctions2_function" "runtask_callback" {
  name        = "runtask-callback-${random_string.suffix.id}"
  description = "runtask-callback handler"
  location    = var.region

  build_config {
    runtime     = "python310"
    entry_point = "callback_handler"
    source {
      storage_source {
        bucket = google_storage_bucket.cloud_functions.name
        object = google_storage_bucket_object.runtask_callback.name
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
resource "google_cloudfunctions2_function_iam_member" "runtask_callback_invoker" {
  project        = google_cloudfunctions2_function.runtask_callback.project
  location       = google_cloudfunctions2_function.runtask_callback.location
  cloud_function = google_cloudfunctions2_function.runtask_callback.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.workflow_runtasks.email}"
}

resource "google_cloud_run_service_iam_member" "runtask_callback_cloud_run_invoker" {
  project  = google_cloudfunctions2_function.runtask_callback.project
  location = google_cloudfunctions2_function.runtask_callback.location
  service  = google_cloudfunctions2_function.runtask_callback.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.workflow_runtasks.email}"
}
