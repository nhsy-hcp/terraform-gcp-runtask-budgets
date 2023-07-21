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
        msg = "Error"

        if payload:
            # Validate request
            request_valid, msg = validate_request(payload)

            if request_valid:
                # Send runtask callback response to TFC
                endpoint = payload["task"]["task_result_callback_url"]
                access_token = payload["task"]["access_token"]

                # Pass access token into header
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-type': 'application/vnd.api+json',
                }

                status = str(payload["result"]["status"])
                message = str(payload["result"]["message"])

                logging.info("headers: {}".format(str(headers)))
                logging.info("payload: {}".format(json.dumps(payload)))

                patch(endpoint, headers, status, message)

                msg = "OK"
                status = 200
        else:
            msg = "Payload missing in request"
            status = 422
            logging.warning(msg)

        return msg, status

    except Exception as e:
        logging.exception("Run Task Callback error: {}".format(e))
        msg = "Internal Run Task Callback error occurred"
        status = 500
        logging.warning(f"{status} - {msg}: {e}")

        return msg, status

def validate_request(payload: dict) -> (bool, str):
    """Validate request values"""

    result = True
    msg = None

    if "task" not in payload:
        msg = "Task detail missing in request"
        logging.warning(msg)
        result = False

    elif "result" not in payload:
        msg = "Result detail missing in request"
        logging.warning(msg)
        result = False

    return result, msg


def patch(url: str, headers: dict, status: str, msg: str) -> int:
    """Calls back to TFC with the result of the run task"""

    # For details of payload and request see
    # https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run-tasks/run-tasks-integration#run-task-callback
    if url and headers and status:
        payload = {
            "data": {
                "type": "task-results",
                "attributes": {
                    "status": status,
                    "message": msg
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
