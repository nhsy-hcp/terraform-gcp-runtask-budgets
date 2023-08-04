import json
import os
import functions_framework
import google.cloud.logging
import logging
import requests

# Setup google cloud logging and ignore errors
if "DISABLE_GOOGLE_LOGGING" not in os.environ:
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
    except google.auth.exceptions.DefaultCredentialsError:
        pass

if 'LOG_LEVEL' in os.environ:
    logging.getLogger().setLevel(os.environ['LOG_LEVEL'])
    logging.info("LOG_LEVEL set to %s" % logging.getLogger().getEffectiveLevel())


@functions_framework.http
def callback_handler(request):
    try:
        logging.info("headers: " + str(request.headers))
        logging.info("payload: " + str(request.get_data()))

        headers = request.headers
        payload = request.get_json(silent=True)
        http_message = "Error"
        http_code = ""

        if payload:
            # Validate request
            request_valid, message = validate_request(payload)

            if request_valid:
                # Send runtask callback response to TFC
                endpoint = payload["task"]["task_result_callback_url"]
                access_token = payload["task"]["access_token"]

                # Pass access token into header
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-type': 'application/vnd.api+json',
                }

                patch_status = str(payload["result"]["status"])
                patch_message = str(payload["result"]["message"])

                logging.info("headers: {}".format(str(headers)))
                logging.info("payload: {}".format(json.dumps(payload)))

                patch(endpoint, headers, patch_status, patch_message)

                http_message = "OK"
                http_code = 200
        else:
            http_message = "Payload missing in request"
            http_code = 422
            logging.warning(f"{http_code} - {http_message}")

        return http_message, http_code

    except Exception as e:
        logging.exception("Run Task Callback error: {}".format(e))
        http_message = "Internal Run Task Callback error occurred"
        http_code = 500
        logging.warning(f"{http_code} - {http_message}: {e}")

        return http_message, http_code


def validate_request(payload: dict) -> (bool, str):
    """Validate request values"""

    result = True
    message = None

    if "task" not in payload:
        message = "Task detail missing in request"
        logging.warning(message)
        result = False

    elif "result" not in payload:
        message = "Result detail missing in request"
        logging.warning(message)
        result = False

    return result, message


def patch(url: str, headers: dict, patch_status: str, patch_message: str) -> int:
    """Calls back to TFC with the result of the run task"""

    # For details of payload and request see
    # https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run-tasks/run-tasks-integration#run-task-callback
    if url and headers and patch_status:
        payload = {
            "data": {
                "type": "task-results",
                "attributes": {
                    "status": patch_status,
                    "message": patch_message
                },
            }
        }

        logging.info(json.dumps(headers))
        logging.info(json.dumps(payload))

        with requests.patch(url, json.dumps(payload), headers=headers) as r:
            logging.info(r)
            r.raise_for_status()

        return r.status_code

    raise TypeError("Missing params")
