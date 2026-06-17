import unittest
from contextlib import redirect_stdout
from io import StringIO

from app.services.submission_service import (
    build_submission_runner_code,
    calculate_score,
    parse_runner_stdout,
)


# Verify the runner wrapper, result parser, and score calculation helpers.
class SubmissionServiceTest(unittest.TestCase):
    # Verify that the generated runner code calls the target exercise function.
    def test_build_submission_runner_code_contains_function_call(self):
        runner_code = build_submission_runner_code(
            student_code="def add_one(value):\n    return value + 1\n",
            function_name="add_one",
            test_cases=[
                {"input": {"value": 1}, "expected_output": 2},
            ],
        )

        self.assertIn("def add_one(value):", runner_code)
        self.assertIn("actual = add_one(**test_input)", runner_code)
        self.assertIn('"expected_output": 2', runner_code)

    # Verify that floating-point rounding noise does not fail numeric test cases.
    def test_build_submission_runner_code_uses_tolerance_for_float_results(self):
        runner_code = build_submission_runner_code(
            student_code="def add_tax(price, rate):\n    return price * (1 + rate)\n",
            function_name="add_tax",
            test_cases=[
                {"input": {"price": 50, "rate": 0.1}, "expected_output": 55.0},
            ],
        )

        output = StringIO()
        with redirect_stdout(output):
            exec(runner_code, {})

        results = parse_runner_stdout(output.getvalue())

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].passed)

    # Verify that boolean inputs are rendered as valid Python values in the runner code.
    def test_build_submission_runner_code_supports_boolean_inputs(self):
        runner_code = build_submission_runner_code(
            student_code=(
                "def greet(name, excited=False):\n"
                "    if excited:\n"
                "        return f'Hello, {name}!'\n"
                "    return f'Hello, {name}.'\n"
            ),
            function_name="greet",
            test_cases=[
                {"input": {"name": "Mia"}, "expected_output": "Hello, Mia."},
                {"input": {"name": "Sam", "excited": True}, "expected_output": "Hello, Sam!"},
                {"input": {"name": "Lee", "excited": False}, "expected_output": "Hello, Lee."},
            ],
        )

        output = StringIO()
        with redirect_stdout(output):
            exec(runner_code, {})

        results = parse_runner_stdout(output.getvalue())

        self.assertEqual(len(results), 3)
        self.assertTrue(all(result.passed for result in results))

    # Verify that stdout JSON from the runner is converted to test result rows.
    def test_parse_runner_stdout_reads_results(self):
        stdout = (
            '{"results": ['
            '{"name": "case 1", "passed": true, "input": {"value": 1}, '
            '"expected_output": 2, "actual_output": 2, "error": ""}'
            "]}\n"
        )

        results = parse_runner_stdout(stdout)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].passed)
        self.assertEqual(results[0].expected_output, 2)

    # Verify that score is the percentage of passed test cases.
    def test_calculate_score_counts_passed_results(self):
        stdout = (
            '{"results": ['
            '{"name": "case 1", "passed": true, "input": {}, '
            '"expected_output": 1, "actual_output": 1, "error": ""},'
            '{"name": "case 2", "passed": false, "input": {}, '
            '"expected_output": 2, "actual_output": 1, "error": ""}'
            "]}\n"
        )

        score = calculate_score(parse_runner_stdout(stdout))

        self.assertEqual(score, 0.5)


if __name__ == "__main__":
    unittest.main()
