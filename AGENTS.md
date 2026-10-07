# AGENTS.md

This file provides guidance to AI coding agents (e.g. Claude Code) when working with code in this repository.

## Project Overview

This is a Terraform Cloud Run Task that provides budget-based deployment control for Google Cloud projects. It prevents Terraform deployments when project labels indicate budget constraints are exceeded (e.g., `tfc-deploy=false`).

## Development Commands

All automation runs through `Taskfile.yml` (`task --list` shows everything).

### Setup & Quality
```bash
task init     # venv, Python deps, pre-commit hooks, terraform init
task lint     # pre-commit (gitleaks, shellcheck, ruff, yamllint) + terraform fmt/validate
task test:ci  # lint + all tests
```

### Cloud Functions Development
```bash
task cf:run FUNCTION=runtask_process    # Start local development server
task cf:build FUNCTION=runtask_process  # Build container with buildpacks (needs pack CLI)
task cf:test FUNCTION=runtask_process   # Test locally with curl
```
Each `cloud_functions/runtask_*` directory also has a Makefile (`make run|build|test`).

### Testing
```bash
task test:cf         # Cloud function unit tests (cloud_functions/tests)
task test:terraform  # Infrastructure tests (tests/) - DEPLOYS real resources, then destroys
```
Some `test:cf` tests call the Resource Manager API and need valid ADC (`gcloud auth application-default login`) plus a default project (`gcloud config set project <id>` or `GOOGLE_CLOUD_PROJECT`).

### Terraform Infrastructure
```bash
task terraform:plan     # terraform plan
task terraform:all      # fmt -> init -> validate -> apply
task terraform:destroy  # terraform destroy
task docs:terraform     # regenerate terraform/README.md (terraform-docs)
```

## Architecture

### Core Components
- **runtask_request**: Validates Terraform Cloud webhooks, triggers async processing
- **runtask_process**: Downloads plan JSON, checks GCP project labels, validates deployments
- **runtask_callback**: Posts results back to Terraform Cloud
- **runtask_echo**: Debug function that echoes requests (not deployed by Terraform)

### Key Files (`cloud_functions/runtask_process/`)
- `googleproject.py`: Google Cloud Resource Manager integration for project labels
- `terraformplan.py`: Terraform plan JSON parsing and project ID extraction
- `terraformcloud.py`: Terraform Cloud API client for plan downloads

### Infrastructure Flow
1. API Gateway receives Terraform Cloud webhook
2. Cloud Workflow orchestrates async processing
3. Functions check project labels against deployment policy
4. Results posted back to Terraform Cloud via callback

## Configuration

### Environment Variables (Cloud Functions)
- `HMAC_KEY`: Terraform Cloud webhook validation (request)
- `RUNTASK_PROJECT`, `RUNTASK_REGION`, `RUNTASK_WORKFLOW`: Workflow target (request; set by Terraform)
- `TFC_ORG`: Optional Terraform Cloud organization filter (request; disabled if unset)
- `WORKSPACE_PREFIX`: Optional workspace name filter (request; disabled if unset)
- `TFC_PROJECT_LABEL`: Project label to check (process; default `tfc-deploy`)
- `LOG_LEVEL`: Optional log level (all functions)

### Terraform Variables
Configure in `terraform/terraform.tfvars`:
```hcl
project_id     = "__DEPLOYMENT_GOOGLE_PROJECT__"
project_viewer = ["__BUDGET_GOOGLE_PROJECT__"] # optional, defaults to []
# region   = "europe-west1" (default)
# hmac_key = "secret" (default - override for real deployments)
```

## Dependencies

- **Python 3.13** (`.python-version`; Cloud Functions runtime `python313`)
- **Flask 3.1.x** / functions-framework 3.x for HTTP handling
- **Terraform 1.10+**; Google providers `~> 7.46`
- **Google Cloud SDK** with authenticated credentials
- **Task** and **pre-commit**; `pack` CLI for buildpacks builds (`gcr.io/buildpacks/builder:google-22`)

## Conventions

- Python deps use exact `==` pins, kept identical across all `requirements.txt` files; Dependabot (`.github/dependabot.yml`) raises weekly PRs for pip, Terraform, GitHub Actions and pre-commit.
- `ruff.toml` pins the lint rule set to `E4, E7, E9, F`; broaden it in a dedicated cleanup change.
- `AGENTS.md` and `.terraform.lock.hcl` are gitignored.

## Key Behaviors

- Deployment allowed when project label `tfc-deploy=true` or missing
- Deployment blocked when project label `tfc-deploy=false`
- Destroy plans always allowed regardless of labels
- No-op plans (no resource changes) always pass
- Organization and workspace filtering applied before processing
