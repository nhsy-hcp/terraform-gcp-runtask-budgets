import logging
import os

import functions_framework
import google.cloud.logging

# Setup google cloud logging and ignore errors
if "DISABLE_GOOGLE_LOGGING" not in os.environ:
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
    except google.auth.exceptions.DefaultCredentialsError:
        pass


if "LOG_LEVEL" in os.environ:
    logging.getLogger().setLevel(os.environ["LOG_LEVEL"])
    logging.info("LOG_LEVEL set to %s" % logging.getLogger().getEffectiveLevel())


def __sanitize_headers(headers) -> dict:
    """Remove sensitive headers from logging"""
    if not headers:
        return {}

    try:
        safe_headers = dict(headers)
    except (TypeError, ValueError):
        # Handle Mock objects in tests
        if hasattr(headers, "items"):
            safe_headers = dict(headers.items())
        else:
            return {}

    sensitive_keys = ["authorization", "x-tfc-task-signature", "x-api-key"]

    for key in list(safe_headers.keys()):
        if key.lower() in sensitive_keys:
            safe_headers[key] = "[REDACTED]"

    return safe_headers


@functions_framework.http
def echo_handler(request):

    try:
        logging.info("headers: " + str(__sanitize_headers(request.headers)))
        logging.info("payload size: %d bytes", len(request.get_data()))

        headers = request.headers
        payload = (request.get_data()).decode("utf-8")

        http_message = "headers:\n"
        http_message += str(headers)
        http_message += "\n\n"
        http_message += "data:\n"
        http_message += payload

        return http_message

    except Exception as e:
        logging.exception("Error: {}".format(e))
        http_message = "Internal error occurred"
        http_code = 500

        return http_message, http_code
