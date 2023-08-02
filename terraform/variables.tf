variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "europe-west1"
}

variable "hmac_key" {
  type    = string
  default = "secret"
}

variable "project_viewer" {
  type    = string
  default = null
}