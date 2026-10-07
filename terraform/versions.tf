terraform {
  required_version = ">= 1.10.0"
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.8"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 7.46"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 7.46"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.6"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.9"
    }
  }
}
