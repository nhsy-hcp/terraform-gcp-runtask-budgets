import logging

import requests


def download_json_plan(access_token: str, plan_json_api_url: str) -> dict:
    """
    Download Terraform plan from TFC API

    :param access_token: TFC API access token
    :param plan_json_api_url: TFC JSON plan URL
    :return: Terraform plan as dict
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.api+json",
    }

    try:
        response = requests.get(plan_json_api_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error("Timeout downloading plan from TFC API")
        return dict()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error downloading plan: {e.response.status_code}")
        return dict()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error downloading plan: {e}")
        return dict()


if __name__ == "__main__":

    access_token = ""
    plan_json_api_url = ""

    plan_json = download_json_plan(access_token, plan_json_api_url)
    import terraformplan

    print(terraformplan.get_project_ids(plan_json))
