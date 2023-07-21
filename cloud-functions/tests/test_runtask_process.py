from unittest.mock import Mock
from runtask_process import main


def test_process_handler():
    req = Mock(get_json=Mock())

    assert main.process_handler(req) in [
        ({'message': 'Google Cloud Runtask Budgets - failed', 'status': 'failed'}, 200),
        ({'message': 'Google Cloud Runtask Budgets - passed', 'status': 'passed'}, 200)
    ]


# def test_print_hello_world():
#     data = {}
#     req = Mock(get_json=Mock(return_value=data), args=data)
#
#     # Call tested function
#     assert main.hello_http(req) == "Hello World!"