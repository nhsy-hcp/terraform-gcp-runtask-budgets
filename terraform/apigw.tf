resource "google_api_gateway_api" "runtasks" {
  provider = google-beta

  api_id       = "apigw-${random_string.suffix.id}"
  display_name = "API Gateway for TFC Run Tasks"
}

resource "google_api_gateway_api_config" "runtasks" {
  provider      = google-beta
  api           = google_api_gateway_api.runtasks.api_id
  api_config_id = "apigw-config-${random_string.suffix.id}"

  gateway_config {
    backend_config {
      google_service_account = google_service_account.apigw_runtasks.email
    }
  }

  openapi_documents {
    document {
      path     = "spec.yaml"
      contents = base64encode(templatefile("files/openapi.yaml", { "request_url" = google_cloudfunctions2_function.runtask_request.url }))
    }
  }
  lifecycle {
    create_before_destroy = false
  }
}

resource "google_api_gateway_gateway" "runtasks" {
  provider   = google-beta
  api_config = google_api_gateway_api_config.runtasks.id
  gateway_id = google_api_gateway_api.runtasks.api_id
  region     = var.region
}