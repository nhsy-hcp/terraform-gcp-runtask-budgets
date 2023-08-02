import json
from jsonpath_ng import jsonpath  # doesn't support filter expressions
from jsonpath_ng.ext import parse
import os
from typing import List


def get_project_ids(plan_json: dict) -> List[str]:
    """
    Return project id's by searching google and google-beta providers.

    :param plan_json: terraform plan json
    :return: project id list
    """

    jsonpath_references_expressions = [
        '$.configuration.provider_config[?(@.name = "google")].expressions.project.references',
        '$.configuration.provider_config[?(@.name = "google-beta")].expressions.project.references'
    ]

    jsonpath_values_expressions = [
        '$.configuration.provider_config[?(@.name = "google")].expressions.project.constant_value',
        '$.configuration.provider_config[?(@.name = "google-beta")].expressions.project.constant_value'
    ]

    project_ids = []
    project_ids.extend(__get_jsonpath_references(plan_json, jsonpath_references_expressions))
    project_ids.extend(__get_jsonpath_values(plan_json, jsonpath_values_expressions))

    unique_project_ids = __unique_list(project_ids)
    # print("unique_project_ids: {}".format(unique_project_ids))

    return unique_project_ids


def __get_jsonpath_references(plan_json: dict, json_expressions: List[str]) -> List[str]:
    """
    Return project id's by references lookup in terraform provider.

    :param plan_json: terraform plan json
    :param json_expressions: terraform provider variable references filters
    :return: project id list
    """
    project_vars = []
    ret_values = []

    for json_expression in json_expressions:
        # print("json_expression: {}".format(json_expression))
        json_expression_project_vars = __flatten_list([match.value for match in parse(json_expression).find(plan_json)])
        # print("json_expression_project_vars: {}".format(json_expression_project_vars))
        project_vars.extend(json_expression_project_vars)
        # print("project_vars: {}".format(project_vars))

    project_vars = __unique_list(project_vars)

    for var in project_vars:
        var = var.replace("var.", "", 1)
        # print("var: {}".format(var))
        ret_values.append(__get_terraform_variable(plan_json, var))

    # print("ret_values {}".format(ret_values))

    return ret_values


def __get_jsonpath_values(plan_json: dict, json_expressions: List[str]) -> List[str]:
    """
    Return project id's by constant value lookup in terraform provider.

    :param plan_json: terraform plan json
    :param json_expressions: terraform provider constant value filters
    :return: project id list
    """

    ret_values = []

    for json_expression in json_expressions:
        # print(json_expression)
        items = [match.value for match in parse(json_expression).find(plan_json)]
        ret_values.extend(items)

    unique_ret_values = __unique_list(ret_values)

    # print(unique_ret_values)
    return unique_ret_values


def __get_terraform_variable(plan_json: dict, terraform_variable: str) -> str:
    """
    Returns value of terraform variable

    :param plan_json: terraform plan json
    :param terraform_variable: terraform variable to lookup
    :return: terraform variable value
    """

    # print("terraform_variable: {}".format(terraform_variable))
    jsonpath_expression = "$.variables.{}.value".format(terraform_variable)
    # print("jsonpath_expression: {}".format(jsonpath_expression))
    terraform_values = [match.value for match in parse(jsonpath_expression).find(plan_json)]
    # print("terraform_values: {}".format(terraform_values))

    if terraform_values:
        terraform_value = terraform_values[0]
    else:
        terraform_value = ""

    return terraform_value


def __flatten_list(lst: List[str]) -> List[str]:
    return [item for sublist in lst for item in (__flatten_list(sublist) if isinstance(sublist, list) else [sublist])]


def __unique_list(lst: List[str]) -> List[str]:
    return list(dict.fromkeys(lst))


if __name__ == "__main__":
    TERRAFORM_BASE = f"{os.path.dirname(__file__)}/../terraform"
    TF_PLAN = f"{os.path.dirname(__file__)}/tests/tfplan.json"

    with open(TF_PLAN) as tfplan_file:
        tfplan = json.load(tfplan_file)
        print(get_project_ids(tfplan))
