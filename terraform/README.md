<!-- BEGIN_TF_DOCS -->
# terraform-gcp-runtask-budgets

## Overview

Deploys Google Cloud resources for the TFC Run Task.

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.4.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | 2.4.0 |
| <a name="provider_google"></a> [google](#provider\_google) | 4.76.0 |
| <a name="provider_google-beta"></a> [google-beta](#provider\_google-beta) | 4.76.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.5.1 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | Project id for deployment | `string` | n/a | yes |
| <a name="input_hmac_key"></a> [hmac\_key](#input\_hmac\_key) | HMAC key for signing requests | `string` | `"secret"` | no |
| <a name="input_project_viewer"></a> [project\_viewer](#input\_project\_viewer) | Project ids to assign viewer access for runtask\_process cloud function service account | `string` | `null` | no |
| <a name="input_region"></a> [region](#input\_region) | Region for deployment | `string` | `"europe-west1"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_gateway_endpoint_uri"></a> [api\_gateway\_endpoint\_uri](#output\_api\_gateway\_endpoint\_uri) | API Gateway runtask endpoint uri |
| <a name="output_cloud_functions_bucket"></a> [cloud\_functions\_bucket](#output\_cloud\_functions\_bucket) | Cloud functions cloud storage bucket |
| <a name="output_runtask_callback_uri"></a> [runtask\_callback\_uri](#output\_runtask\_callback\_uri) | Callback cloud function uri |
| <a name="output_runtask_process_uri"></a> [runtask\_process\_uri](#output\_runtask\_process\_uri) | Process cloud function uri |
| <a name="output_runtask_request_uri"></a> [runtask\_request\_uri](#output\_runtask\_request\_uri) | Request cloud function uri |
<!-- END_TF_DOCS -->