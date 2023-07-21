
.PHONY: all
all: fmt init validate apply

.PHONY: fmt
fmt:
	terraform fmt

.PHONY: init
init: fmt
	terraform init

.PHONY: validate
validate: init
	terraform validate

.PHONY: plan
plan: init
	terraform plan

.PHONY: apply
apply: init
	terraform apply -auto-approve

.PHONY: replace
replace: init
	terraform apply -auto-approve -replace=module.tfe.aws_instance.this[0] -replace=null_resource.tfe

.PHONY: destroy
destroy: init
	terraform destroy -auto-approve

.PHONY: clean
clean:
	rm -rf ./terraform
	rm terraform.tfstate*
