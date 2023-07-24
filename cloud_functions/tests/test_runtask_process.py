import os
import sys
sys.path.insert(0, f"{os.path.dirname(__file__)}/../runtask_process")

from unittest.mock import Mock
from runtask_process import main


def test_process_handler():
    data = {
        "workspace_name": "00000"
    }

    req = Mock(get_json=Mock(return_value=data), args=data)

    assert main.process_handler(req) == ({'message': 'Google Cloud Runtask Budgets - Google project label lookup failed', 'status': 'failed'}, 200)


# def test_print_hello_world():
#     data = {}
#     req = Mock(get_json=Mock(return_value=data), args=data)
#
#     # Call tested function
#     assert main.hello_http(req) == "Hello World!"