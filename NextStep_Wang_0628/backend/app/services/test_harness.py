from __future__ import annotations

import json
from typing import Any


def build_python_test_runner_code(
    student_code: str,
    function_name: str,
    test_cases: list[dict[str, Any]],
) -> str:
    test_cases_json = json.dumps(test_cases, ensure_ascii=False)
    test_cases_literal = repr(test_cases_json)

    return (
        f"{student_code}\n\n"
        "import json\n"
        "import math\n"
        "import traceback\n"
        "import time\n\n"
        "def __nextstep_is_number(value):\n"
        "    return isinstance(value, (int, float)) and not isinstance(value, bool)\n\n"
        "def __nextstep_values_equal(actual, expected):\n"
        "    if __nextstep_is_number(actual) and __nextstep_is_number(expected):\n"
        "        return math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-6)\n"
        "    if isinstance(actual, list) and isinstance(expected, list):\n"
        "        return len(actual) == len(expected) and all(\n"
        "            __nextstep_values_equal(a, e) for a, e in zip(actual, expected)\n"
        "        )\n"
        "    if isinstance(actual, dict) and isinstance(expected, dict):\n"
        "        return actual.keys() == expected.keys() and all(\n"
        "            __nextstep_values_equal(actual[key], expected[key]) for key in expected\n"
        "        )\n"
        "    return actual == expected\n\n"
        "def __nextstep_run_tests():\n"
        f"    test_cases = json.loads({test_cases_literal})\n"
        "    results = []\n"
        "    for index, test_case in enumerate(test_cases, start=1):\n"
        "        test_input = test_case.get('input')\n"
        "        expected = test_case.get('expected_output')\n"
        "        actual = None\n"
        "        error = ''\n"
        "        passed = False\n"
        "        started_at = time.perf_counter()\n"
        "        try:\n"
        "            if isinstance(test_input, dict):\n"
        f"                actual = {function_name}(**test_input)\n"
        "            elif isinstance(test_input, list):\n"
        f"                actual = {function_name}(*test_input)\n"
        "            else:\n"
        f"                actual = {function_name}(test_input)\n"
        "            passed = __nextstep_values_equal(actual, expected)\n"
        "        except Exception:\n"
        "            error = traceback.format_exc()\n"
        "        runtime_ms = int((time.perf_counter() - started_at) * 1000)\n"
        "        results.append({\n"
        "            'id': f'case_{index}',\n"
        "            'label': f'case {index}',\n"
        "            'input': test_input,\n"
        "            'expected': expected,\n"
        "            'actual': actual,\n"
        "            'hidden': False,\n"
        "            'passed': passed,\n"
        "            'runtimeMs': runtime_ms,\n"
        "            'error': error,\n"
        "        })\n"
        "    print(json.dumps({'results': results}, ensure_ascii=False))\n\n"
        "__nextstep_run_tests()\n"
    )


def parse_runner_stdout(stdout: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(stdout.strip())
    except json.JSONDecodeError:
        return []

    return list(payload.get("results", []))


def calculate_score(test_results: list[dict[str, Any]]) -> float:
    if not test_results:
        return 0.0

    passed_count = sum(1 for result in test_results if result.get("passed"))
    return round(passed_count / len(test_results), 2)


def format_case_value(value: Any) -> str:
    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)
