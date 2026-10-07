variable "project_id" {
  description = "Project id for deployment"
  type        = string
}

variable "region" {
  description = "Region for deployment"
  type        = string
  default     = "europe-west1"
}

variable "hmac_key" {
  description = "HMAC key shared with the TFC Run Task for signing requests"
  type        = string
  sensitive   = true
}

variable "project_viewer" {
  description = "Project ids to assign viewer access for runtask_process cloud function service account"
  type        = list(string)
  default     = []
  nullable    = false
}
