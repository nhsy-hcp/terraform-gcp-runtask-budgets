import logging
import os
import functions_framework
import google.cloud.logging
import googleproject
import terraformcloud
import terraformplan
from typing import List

# Setup google cloud logging and ignore errors if authentication fails
if "DISABLE_GOOGLE_LOGGING" not in os.environ:
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
    except google.auth.exceptions.DefaultCredentialsError:
        pass

if "LOG_LEVEL" in os.environ:
    logging.getLogger().setLevel(os.environ["LOG_LEVEL"])
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

        payload = request.get_json(silent=True)
        http_msg = "{}"

        if payload and ("access_token" in payload and "plan_json_api_url" in payload):
            access_token = payload["access_token"]
            plan_json_api_url = payload["plan_json_api_url"]

            project_ids, msg = __get_project_ids(access_token, plan_json_api_url)

            if project_ids:
                validate_result, validate_msg = __validate_project_ids(project_ids)
            else:
                validate_result = False
                validate_msg = msg

            runtask_msg = "Google Cloud Runtask Budgets - {}".format(validate_msg)

            if validate_result:
                runtask_status = "passed"
            else:
                runtask_status = "failed"

            http_msg = {"message": runtask_msg, "status": runtask_status}

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


def __validate_project_ids(project_ids: List[str]) -> (bool, str):
    result = False
    disabled_project_ids = []

    try:
        proj = googleproject.GoogleProject()
        for project_id in project_ids:
            proj.get(project_id)
            if proj.label(TFC_PROJECT_LABEL).lower() == "false":
                disabled_project_ids.append(project_id)

        if disabled_project_ids:
            msg = "TFC deployments disabled: {}".format(", ".join(disabled_project_ids))
        else:
            msg = "TFC deployments enabled: {}".format(", ".join(project_ids))
            result = True

    except Exception as e:
        logging.exception("Warning: {}".format(e))
        msg = "Google project label lookup failed: {}".format(", ".join(project_ids))

    return result, msg


def __get_project_ids(access_token, plan_json_api_url) -> (List[str], str):
    msg = ""
    project_ids = []

    try:
        plan_json = terraformcloud.download_json_plan(access_token, plan_json_api_url)
        # logging.info("plan_json: " + str(plan_json))
        project_ids = terraformplan.get_project_ids(plan_json)
        logging.info("project_ids: " + str(project_ids))
    except Exception as e:
        logging.warning("Warning: {}".format(e))
        msg = "TFC plan download or parse failed"

    return project_ids, msg
