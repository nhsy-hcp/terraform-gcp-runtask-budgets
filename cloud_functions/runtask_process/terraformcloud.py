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

    response = requests.get(plan_json_api_url, headers=headers)
    # print(response.status_code)
    # print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        return dict()


if __name__ == "__main__":

    access_token = ""
    plan_json_api_url = ""

    plan_json = download_json_plan(access_token, plan_json_api_url)
    import terraformplan
    print(terraformplan.get_project_ids(plan_json))
