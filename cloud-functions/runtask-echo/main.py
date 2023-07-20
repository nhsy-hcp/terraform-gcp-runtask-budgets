import os
import functions_framework
import logging
import google.cloud.logging

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
def echo_handler(request):

    try:
        logging.info("headers: " + str(request.headers))
        logging.info("payload: " + str((request.get_data()).decode("utf-8")))

        headers = request.headers
        payload = (request.get_data()).decode("utf-8")

        msg = "headers:\n"
        msg += str(headers)
        msg += "\n\n"
        msg += "data:\n"
        msg += payload

        return msg

    except Exception as e:
        logging.exception("Error: {}".format(e))
        msg = "Internal error occurred"
        status = 500

        return msg, status
