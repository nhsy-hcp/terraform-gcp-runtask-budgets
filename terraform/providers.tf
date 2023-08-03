provider "google" {
  project = var.project_id
  region  = "europe-west1"
}

provider "google-beta" {
  project = var.project_id
  region  = "europe-west1"
}