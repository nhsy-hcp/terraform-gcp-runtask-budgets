PROJECT = $(CURDIR)

all: run

.PHONY: build run docker test test-remote

build:
	pack build \
	 --builder gcr.io/buildpacks/builder:v1 \
	 --env GOOGLE_FUNCTION_SIGNATURE_TYPE=http \
	 --env GOOGLE_FUNCTION_TARGET=process_handler \
	 runtask_callback

run:
	DISABLE_GOOGLE_LOGGING=1 HMAC_KEY=secret functions-framework --target process_handler --debug

docker:
	docker run --rm -p 8080:8080 runtask_callback

test:
	curl http://127.0.0.1:8080 -w "%{http_code}" -X POST -H 'Content-Type: application/json' -d @testing/data.json

test-remote:
	curl $(URL) -w "%{http_code}" \
		-X POST -H 'Content-Type: application/json' \
		-H "Authorization: Bearer $(TOKEN)" \
		-d @testing/data.json
