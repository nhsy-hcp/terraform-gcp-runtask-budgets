import json
import os

from runtask_process import terraformplan

TERRAFORM_BASE = f"{os.path.dirname(__file__)}/../terraform"
TF_PLAN = f"{os.path.dirname(__file__)}/../runtask_process/tests/tfplan.json"


def test_ger_project_ids():
    with open(TF_PLAN) as tfplan_file:
        tfplan = json.load(tfplan_file)

        project_ids = terraformplan.get_project_ids(tfplan)

        assert len(project_ids) > 0
