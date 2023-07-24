import os
# import sys
# sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_process")

import subprocess
import requests
from requests.packages.urllib3.util.retry import Retry


def test_process_integration():
    port = os.getenv(
        "PORT", 8090
    )  # Each functions framework instance needs a unique port

    process = subprocess.Popen(
        ["functions-framework", "--target", "process_handler", "--port", str(port)],
        cwd=f"{os.path.dirname(__file__)}/../runtask_process",
        stdout=subprocess.PIPE,
        env=os.environ
    )

    url = f"http://localhost:{port}"

    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=retry_policy)

    session = requests.Session()
    session.mount(url, retry_adapter)

    data = "{}"
    response = session.post(url, json=data)

    # Stop the functions framework process
    process.kill()
    process.wait()


    assert response.status_code == 422
    assert response.text  == "{}"