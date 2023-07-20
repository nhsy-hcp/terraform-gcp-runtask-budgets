import os
import functions_framework
import google.cloud.logging
import logging
import random

# Setup google cloud logging and ignore errors
if "DISABLE_REMOTE_LOGGING" not in os.environ:
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
    except google.auth.exceptions.DefaultCredentialsError:
        pass

if 'LOG_LEVEL' in os.environ:
    logging.getLogger().setLevel(os.environ['LOG_LEVEL'])
    logging.info("LOG_LEVEL set to %s" % logging.getLogger().getEffectiveLevel())

@functions_framework.http
def process_handler(request):

    try:
        logging.info("headers: " + str(request.headers))
        logging.info("payload: " + str(request.get_data()))

        headers = request.headers
        payload = request.get_json(silent=True)

        result = random.choice(["passed", "failed"])

        if payload:
            body = {
                "message": "GCP Runtask Budgets - {}".format(result),
                "status": result
            }

            msg = body
            status = 200

        else:
            msg = "Payload missing in request"
            status = 422
            logging.warning(msg)

        logging.info(f"{status} - {msg}")

        return msg, status

    except Exception as e:
        logging.exception("Run Task Process error: {}".format(e))
        msg = "Internal Run Task Process error occurred"
        status = 500
        logging.warning(f"{status} - {msg}: {e}")

        return msg, status

