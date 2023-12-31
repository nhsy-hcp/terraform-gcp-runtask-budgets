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
        http_message = "{}"

        # Check if payload is valid
        if payload and ("access_token" in payload and "plan_json_api_url" in payload):
            access_token = payload["access_token"]
            plan_json_api_url = payload["plan_json_api_url"]

            # Download terraform plan from TFC
            plan_json, plan_json_msg = __get_plan_json(access_token, plan_json_api_url)
            # print("plan_json: " + str(plan_json))

            if plan_json:
                project_ids, project_ids_msg = __get_project_ids(plan_json)
                validate_plan_result, validate_plan_msg = __validate_plan(plan_json)

                # Destroy plan overrides
                if validate_plan_result:
                    validate_result = True
                    validate_msg = validate_plan_msg
                # Projects ids  found in terraform plan
                elif project_ids:
                    validate_result, validate_msg = __validate_project_ids(project_ids)
                # Error occurred return message
                else:
                    validate_result = False
                    validate_msg = project_ids_msg
            # Error occurred return message
            else:
                validate_result = False
                validate_msg = plan_json_msg

            runtask_message = validate_msg

            if validate_result:
                runtask_status = "passed"
            else:
                runtask_status = "failed"

            http_message = {"message": runtask_message, "status": runtask_status}
            http_code = 200

        else:
            runtask_message = "Payload missing in request"
            runtask_status = "failed"
            http_message = {"message": runtask_message, "status": runtask_status}
            http_code = 422
            logging.warning(payload)

        logging.info(f"{http_code} - {http_message}")

        return http_message, http_code
    # Error occurred return message
    except Exception as e:
        logging.exception("Run Task Process error: {}".format(e))
        http_message = "Internal Run Task Process error occurred"
        http_code = 500
        logging.warning(f"{http_code} - {http_message}: {e}")

        return http_message, http_code


def __validate_plan(plan_json) -> (bool, str):
    """
    Check if plan is a destroy or noop plan and override project flags

    :param plan_json: terraform plan json string
    :return: true if resources are destroyed only, false otherwise

    """
    validate_plan_result, validate_plan_msg = terraformplan.validate_plan(plan_json)
    message = "TFC deployments override: {}".format(validate_plan_msg)

    return validate_plan_result, message


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
            message = "TFC deployments disabled: {}".format(", ".join(disabled_project_ids))
        else:
            message = "TFC deployments enabled: {}".format(", ".join(project_ids))
            result = True

    except Exception as e:
        logging.exception("Warning: {}".format(e))
        message = "Google project label lookup failed: {}".format(", ".join(project_ids))

    return result, message


def __get_project_ids(plan_json: dict) -> (List[str], str):
    message = ""
    project_ids = []

    try:
        project_ids = terraformplan.get_project_ids(plan_json)
        logging.info("project_ids: " + str(project_ids))
    except Exception as e:
        logging.warning("Warning: {}".format(e))
        message = "TFC plan parse failed"

    return project_ids, message


def __get_plan_json(access_token: str, plan_json_api_url: str) -> (dict, str):
    message = ""
    plan_json = {}

    try:
        plan_json = terraformcloud.download_json_plan(access_token, plan_json_api_url)
        # logging.info("plan_json: " + str(plan_json))
    except Exception as e:
        logging.warning("Warning: {}".format(e))
        message = "TFC plan download failed"

    return plan_json, message
