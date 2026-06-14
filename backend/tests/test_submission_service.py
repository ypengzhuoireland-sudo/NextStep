import unittest

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
