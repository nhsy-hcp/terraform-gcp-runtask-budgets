output "runtask_callback_uri" {
  value = google_cloudfunctions2_function.runtask_callback.url
}

output "runtask_process_uri" {
  value = google_cloudfunctions2_function.runtask_process.url
}

output "runtask_request_uri" {
  value = google_cloudfunctions2_function.runtask_request.url
}

output "cloud_functions_bucket" {
  value = google_storage_bucket.cloud_functions.id
}