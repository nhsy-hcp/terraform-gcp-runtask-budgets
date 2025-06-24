import logging
import os
from typing import List

import functions_framework
import google.cloud.logging
import googleproject
import terraformcloud
import terraformplan

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


def __validate_request_size(request) -> (bool, str):
    """Validate incoming request size"""
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB limit

    try:
        content_length = request.content_length
        if (
            content_length
            and isinstance(content_length, int)
            and content_length > MAX_PAYLOAD_SIZE
        ):
            return (
                False,
                f"Request too large: {content_length} bytes (max: {MAX_PAYLOAD_SIZE})",
            )
    except (TypeError, AttributeError):
        # Handle Mock objects in tests - assume valid size
        pass

    return True, "Valid size"


if "TFC_PROJECT_LABEL" in os.environ:
    TFC_PROJECT_LABEL = os.environ["TFC_PROJECT_LABEL"]
else:
    TFC_PROJECT_LABEL = "tfc-deploy"


def __validate_process_payload(payload) -> (bool, str):
    """Comprehensive payload validation"""
    if not payload:
        return False, "Empty payload"

    required_fields = ["access_token", "plan_json_api_url"]
    for field in required_fields:
        if field not in payload:
            return False, f"Missing required field: {field}"
        if not payload[field] or not isinstance(payload[field], str):
            return False, f"Invalid {field} format"

    # Validate URL format
    if not payload["plan_json_api_url"].startswith("https://"):
        return False, "Invalid plan_json_api_url format"

    # Validate access token format (basic check)
    if len(payload["access_token"]) < 10:
        return False, "Invalid access_token format"

    return True, "Valid"


@functions_framework.http
def process_handler(request):
    try:
        logging.info("headers: " + str(__sanitize_headers(request.headers)))
        logging.info("payload size: %d bytes", len(request.get_data()))

        # Validate request size first
        size_valid, size_msg = __validate_request_size(request)
        if not size_valid:
            return {"message": size_msg, "status": "failed"}, 413

        payload = request.get_json(silent=True)
        http_message = "{}"

        # Check if payload is valid
        payload_valid, payload_msg = __validate_process_payload(payload)
        if payload_valid:
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
            runtask_message = payload_msg
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
    """
    Validates a list of project IDs by checking if the TFC deployments are enabled for each project.

    Parameters:
        project_ids (List[str]): A list of project IDs to validate.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating if the validation was successful and a string message.

    Raises:
        Exception: If there is an error while performing the validation.
    """
    result = False
    disabled_project_ids = []

    try:
        proj = googleproject.GoogleProject()
        for project_id in project_ids:
            proj.get(project_id)
            if proj.label(TFC_PROJECT_LABEL).lower() == "false":
                disabled_project_ids.append(project_id)

        if disabled_project_ids:
            message = "TFC deployments disabled: {}".format(
                ", ".join(disabled_project_ids)
            )
        else:
            message = "TFC deployments enabled: {}".format(", ".join(project_ids))
            result = True

    except Exception as e:
        logging.exception("Warning: {}".format(e))
        message = "Google project label lookup failed: {}".format(
            ", ".join(project_ids)
        )

    return result, message


def __get_project_ids(plan_json: dict) -> (List[str], str):
    """
    Get the project IDs from the given plan JSON.

    Args:
        plan_json (dict): The plan JSON containing the project IDs.

    Returns:
        tuple: A tuple containing a list of project IDs and a message string.
            - project_ids (List[str]): A list of project IDs extracted from the plan JSON.
            - message (str): A message string indicating the success or failure of the operation.
    """

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
    """
    Retrieves the JSON representation of a Terraform plan from the Terraform Cloud API.

    Args:
        access_token (str): The access token to authenticate with the Terraform Cloud API.
        plan_json_api_url (str): The URL of the Terraform plan JSON API.

    Returns:
        tuple: A tuple containing the plan JSON dictionary and a message string.
               The plan JSON dictionary represents the retrieved Terraform plan.
               The message string contains an error message if the plan download failed, otherwise it is an empty string.
    """

    message = ""
    plan_json = {}

    try:
        plan_json = terraformcloud.download_json_plan(access_token, plan_json_api_url)
        # logging.info("plan_json: " + str(plan_json))
    except Exception as e:
        logging.warning("Warning: {}".format(e))
        message = "TFC plan download failed"

    return plan_json, message
