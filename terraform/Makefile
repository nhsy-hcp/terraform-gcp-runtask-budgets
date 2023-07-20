
.PHONY: all
all: fmt validate apply

.PHONY: fmt
fmt:
	terraform fmt

.PHONY: validate
validate:
	terraform init
	terraform validate

.PHONY: apply
apply:
	terraform apply -auto-approve

.PHONY: replace
replace:
	terraform apply -auto-approve -replace=module.tfe.aws_instance.this[0] -replace=null_resource.tfe

.PHONY: destroy
destroy:
	terraform destroy -auto-approve

.PHONY: clean
clean:
	rm -rf ./terraform
	rm terraform.tfstate*
