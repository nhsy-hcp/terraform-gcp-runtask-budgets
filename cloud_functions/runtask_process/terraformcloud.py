import requests
import logging
import os
import google.cloud.logging

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


def download_json_plan(access_token: str, plan_json_api_url: str) -> dict:
    plan_json = dict()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.api+json",
    }

    response = requests.get(plan_json_api_url, headers=headers)
    logging.info(response.status_code)
    logging.info(response.text)
    if response.status_code == 200:
        plan_json = response.json()
    else:
        logging.info("Failed to get plan details.")

    return plan_json


if __name__ == "__main__":

    access_token = ""
    plan_json_api_url = ""

    plan_json = download_json_plan(access_token, plan_json_api_url)
    import terraformplan
    print(terraformplan.get_project_ids(plan_json))
