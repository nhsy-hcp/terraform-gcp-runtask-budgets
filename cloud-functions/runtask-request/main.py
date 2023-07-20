import json
import os
from flask import jsonify, make_response
import functions_framework
import logging
import hmac
import hashlib

import google.cloud.logging
from google.cloud import workflows_v1
from google.cloud.workflows import executions_v1
from google.cloud.workflows.executions_v1 import Execution
from google.cloud.workflows.executions_v1.types import executions

# Setup google cloud logging and ignore errors
if "DISABLE_GOOGLE_LOGGING" not in os.environ:
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
    except google.auth.exceptions.DefaultCredentialsError:
        pass

if "TFC_ORG" in os.environ:
    TFC_ORG = os.environ["TFC_ORG"]
else:
    TFC_ORG = False

if "WORKSPACE_PREFIX" in os.environ:
    WORKSPACE_PREFIX = os.environ["WORKSPACE_PREFIX"]
else:
    WORKSPACE_PREFIX = False


if "HMAC_KEY" in os.environ:
    HMAC_KEY = os.environ["HMAC_KEY"]
else:
    HMAC_KEY = False

RUNTASK_STAGES = ["pre_plan", "post_plan", "test"]

if "RUNTASK_PROJECT" in os.environ:
    RUNTASK_PROJECT = os.environ["RUNTASK_PROJECT"]
else:
    RUNTASK_PROJECT = False

if "RUNTASK_REGION" in os.environ:
    RUNTASK_REGION = os.environ["RUNTASK_REGION"]
else:
    RUNTASK_REGION = False

if "RUNTASK_WORKFLOW" in os.environ:
    RUNTASK_WORKFLOW = os.environ["RUNTASK_WORKFLOW"]
else:
    RUNTASK_WORKFLOW = False

if 'LOG_LEVEL' in os.environ:
    logging.getLogger().setLevel(os.environ['LOG_LEVEL'])
    logging.info("LOG_LEVEL set to %s" % logging.getLogger().getEffectiveLevel())

@functions_framework.http
def request_handler(request):

    try:
        logging.info("headers: " + str(request.headers))
        logging.info("payload: " + str(request.get_data()))

        headers = request.headers
        payload = request.get_json(silent=True)
        # request_args = request.args
        status = 422

        if not HMAC_KEY:
            msg = "HMAC key environment variable missing on server"
            status = 500
            logging.error(msg)
        elif not RUNTASK_PROJECT:
            msg = "Project environment variable missing on server"
            status = 500
            logging.error(msg)
        elif not RUNTASK_REGION:
            msg = "Region environment variable missing on server"
            status = 500
            logging.error(msg)
        elif not RUNTASK_WORKFLOW:
            msg = "Workflow name environment variable missing on server"
            status = 500
            logging.error(msg)
        elif payload:
            result, msg = __validate_request(headers, payload)
            if result:
                # Check HMAC signature
                signature = headers['x-tfc-task-signature']
                # Need to use request.get_data() for hmac digest
                if __validate_hmac(HMAC_KEY, request.get_data(), signature):
                    __execute_workflow(payload)
                    msg = "OK"
                    status = 200
                else:
                    msg = "HMAC signature invalid"
                    logging.warning(msg)
        else:
            status = 200
            msg = "Payload missing in request"

        logging.info(f"{status} - {msg}")

        return msg, status

    except Exception as e:
        logging.exception("Run Task Request error: {}".format(e))
        msg = "Internal Run Task Request error occurred"
        status = 500
        logging.warning(f"{status} - {msg}: {e}")

        return msg, status

def __validate_request(headers, payload) -> (bool, str):
    """Validate request values"""

    result = True
    msg = "OK"

    if headers is None:
        msg = "Headers missing in request"
        logging.warning(msg)
        result = False

    elif payload is None:
        msg = "Payload missing in request"
        logging.warning(msg)
        result = False

    elif "x-tfc-task-signature" not in headers:
        msg = "TFC Task signature missing"
        logging.warning(msg)
        result = False

    elif TFC_ORG and payload["organization_name"] != TFC_ORG:
        msg = "TFC Org verification failed : {}".format(payload["organization_name"])
        logging.warning(msg)
        result = False

    elif WORKSPACE_PREFIX and not (str(payload["workspace_name"]).startswith(WORKSPACE_PREFIX)):
        msg = "TFC workspace prefix verification failed : {}".format(payload["workspace_name"])
        logging.warning(msg)
        result = False

    elif RUNTASK_STAGES and not (payload["stage"] in RUNTASK_STAGES):
        msg = "TFC Runtask stage verification failed: {}".format(payload["stage"])
        logging.warning(msg)
        result = False

    return result, msg


def __validate_hmac(key: str, payload: str, signature: str) -> bool:
    """Returns true if the x-tfc-task-signature header matches the SHA512 digest of the payload"""

    digest = hmac.new(bytes(key, 'utf-8'), msg=payload, digestmod=hashlib.sha512).hexdigest()
    result = hmac.compare_digest(digest, signature)

    if not result:
        logging.warning(f"HMAC mismatch, digest: {digest}, signature: {signature}")

    return result


def __execute_workflow(payload: dict, project: str = RUNTASK_PROJECT, location: str = RUNTASK_REGION, workflow: str = RUNTASK_WORKFLOW) -> Execution:
    """Execute a workflow and print the execution results.

    A workflow consists of a series of steps described using the Workflows syntax, and can be written in either YAML or JSON.

    Args:
        project: The Google Cloud project id which contains the workflow to execute.
        location: The location for the workflow
        workflow: The ID of the workflow to execute.

    Returns:
        The execution response.
    """

    arguments = payload

    execution = Execution(argument=json.dumps(arguments))

    # Set up API clients.
    execution_client = executions_v1.ExecutionsClient()
    workflows_client = workflows_v1.WorkflowsClient()

    # Construct the fully qualified location path.
    parent = workflows_client.workflow_path(project, location, workflow)

    # Execute the workflow.
    response = execution_client.create_execution(parent=parent, execution=execution)
    logging.info(f"Created execution: {response.name}")
    execution = execution_client.get_execution(request={"name": response.name})

    return execution
