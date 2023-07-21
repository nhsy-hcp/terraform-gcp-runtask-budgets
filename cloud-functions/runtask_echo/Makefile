all: run

.PHONY: build run docker test test-remote deploy destroy

build:
	pack build \
	 --builder gcr.io/buildpacks/builder:v1 \
	 --env GOOGLE_FUNCTION_SIGNATURE_TYPE=http \
	 --env GOOGLE_FUNCTION_TARGET=echo_handler \
	 runtask_request

run:
	PORT=8081 LOG_LEVEL=INFO DISABLE_GOOGLE_LOGGING=1 functions-framework --target echo_handler --debug

docker:
	docker run --rm -p 8080:8080 runtask_request

test:
	curl -s http://127.0.0.1:8081 -w "%{http_code}" -X POST -H 'Content-Type: application/json' -d @testing/data.json

test-remote:
	curl $(URL) -w "%{http_code}" -X POST -H 'Content-Type: application/json' -d @testing/data.json

deploy:
	gcloud functions deploy runtask-echo \
		--gen2 \
		--region=europe-west1 \
		--runtime=python310 \
		--source=. \
		--entry-point=echo_handler \
		--trigger-http \
		--allow-unauthenticated

destroy:
	gcloud functions delete runtask-echo --region=europe-west1 --quiet
