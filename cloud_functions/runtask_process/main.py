import logging
import os
import functions_framework
import google.cloud.logging
import googleproject

# Setup google cloud logging and ignore errors if authentication fails
if "DISABLE_GOOGLE_LOGGING" not in os.environ:
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
    except google.auth.exceptions.DefaultCredentialsError:
        pass

if 'LOG_LEVEL' in os.environ:
    logging.getLogger().setLevel(os.environ['LOG_LEVEL'])
    logging.info("LOG_LEVEL set to %s" % logging.getLogger().getEffectiveLevel())

if "TFC_PROJECT_LABEL" in os.environ:
    TFC_PROJECT_LABEL = os.environ["TFC_PROJECT_LABEL"]
else:
    TFC_PROJECT_LABEL = "tfc-deploy"

@functions_framework.http
def process_handler(request):

    try:
        logging.info("headers: " + str(request.headers))
        logging.info("payload: " + str(request.get_data()))

        headers = request.headers
        payload = request.get_json(silent=True)
        http_msg = "{}"

        if payload and "workspace_name" in payload:

            project_id = payload["workspace_name"]
            validate_result, validate_msg = validate_deployment(project_id)
            runtask_msg = "Google Cloud Runtask Budgets - {}".format(validate_msg)

            if validate_result:
                runtask_status = "passed"
            else:
                runtask_status = "failed"

            http_msg = {
                "message": runtask_msg,
                "status": runtask_status
            }

            http_code = 200

        else:
            msg = "Payload missing in request"
            http_code = 422
            logging.warning(payload)

        logging.info(f"{http_code} - {http_msg}")

        return http_msg, http_code

    except Exception as e:
        logging.exception("Run Task Process error: {}".format(e))
        msg = "Internal Run Task Process error occurred"
        status = 500
        logging.warning(f"{status} - {msg}: {e}")

        return msg, status


def validate_deployment(project_id: str) -> (bool, str):

    msg = ""
    result = False
    try:
        proj = googleproject.GoogleProject()
        proj.get(project_id)

        if proj.label(TFC_PROJECT_LABEL).lower() == "true":
            result = True
            msg = "TFC deployments enabled"
        else:
            msg = "TFC deployments disabled"

    except Exception as e:
        logging.exception("Warning: {}".format(e))
        # print("Error: {}".format(e))
        msg = "Google project label lookup failed"

    return result, msg
