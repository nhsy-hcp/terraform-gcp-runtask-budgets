output "runtask_callback_uri" {
  value = google_cloudfunctions2_function.runtask_callback.url
}

output "runtask_request_uri" {
  value = google_cloudfunctions2_function.runtask_request.url
}