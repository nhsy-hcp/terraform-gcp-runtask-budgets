import json
import os
import subprocess

import requests
from requests.packages.urllib3.util.retry import Retry

# import sys
# sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_process")


def test_process_integration():
    port = os.getenv(
        "PORT", 8090
    )  # Each functions framework instance needs a unique port

    process = subprocess.Popen(
        ["functions-framework", "--target", "process_handler", "--port", str(port)],
        cwd=f"{os.path.dirname(__file__)}/../runtask_process",
        stdout=subprocess.PIPE,
        env=os.environ,
    )

    url = f"http://localhost:{port}"

    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=retry_policy)

    session = requests.Session()
    session.mount(url, retry_adapter)

    data = {
        "access_token": "0123456789abcdef",
        "plan_json_api_url": "https://app.terraform.io/api/v1/plan",
    }

    response = session.post(url, json=data)

    # Stop the functions framework process
    process.kill()
    process.wait()

    assert response.status_code == 200
    assert response.text == ('{"message":"","status":"failed"}\n')
