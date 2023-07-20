resource "google_service_account" "cloud_function_runtasks" {
  account_id = "cloud-function-runtasks"
}

resource "google_service_account" "workflow_runtasks" {
  account_id = "workflow-runtasks"
}