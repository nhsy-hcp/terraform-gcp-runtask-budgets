output "runtask_callback_uri" {
  description = "Callback cloud function uri"
  value       = google_cloudfunctions2_function.runtask_callback.url
}

output "runtask_process_uri" {
  description = "Process cloud function uri"
  value       = google_cloudfunctions2_function.runtask_process.url
}

output "runtask_request_uri" {
  description = "Request cloud function uri"
  value       = google_cloudfunctions2_function.runtask_request.url
}

output "cloud_functions_bucket" {
  description = "Cloud functions cloud storage bucket"
  value       = google_storage_bucket.cloud_functions.id
}

output "api_gateway_endpoint_uri" {
  description = "API Gateway runtask endpoint uri"
  value       = "https://${google_api_gateway_gateway.runtasks.default_hostname}/runtask-budgets"
}
