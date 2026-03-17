terraform {
  required_version = ">= 1.4.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.23.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 7.23.0"
    }
  }
}
