import unittest

from app.schemas.executions import ExecutionRunRequest
from app.services.execution_service import build_judge0_payload, execute_code_request, normalize_judge0_response


class ExecutionServiceTest(unittest.TestCase):
    # Verify that Python execution requests are converted to the Judge0 payload shape.
    def test_build_judge0_payload_uses_python_language_id(self):
        request = ExecutionRunRequest(
            code='print("hello")',
            language="python",
            stdin="",
        )

        payload = build_judge0_payload(request, python_language_id=71)

        self.assertEqual(payload["language_id"], 71)
        self.assertEqual(payload["source_code"], 'print("hello")')
        self.assertEqual(payload["stdin"], "")

    # Verify local development can execute Python without a Judge0 API key.
    def test_execute_code_request_mock_mode_runs_python_locally(self):
        request = ExecutionRunRequest(
            code='print("hello")',
            language="python",
            stdin="",
        )

        response = execute_code_request(request, runner_mode="mock")

        self.assertEqual(response["status"]["id"], 3)
        self.assertEqual(response["stdout"], "hello\n")
        self.assertEqual(response["stderr"], "")

    # Verify that accepted Judge0 output is marked as passed when stdout matches.
    def test_normalize_judge0_response_marks_passed_when_output_matches(self):
        request = ExecutionRunRequest(
            code='print("hello")',
            language="python",
            expected_output="hello",
        )
        response = {
            "stdout": "hello\n",
            "stderr": None,
            "compile_output": None,
            "message": None,
            "time": "0.01",
            "memory": 1024,
            "token": "abc",
            "status": {"id": 3, "description": "Accepted"},
        }

        result = normalize_judge0_response(response, request)

        self.assertTrue(result.passed)
        self.assertEqual(result.stdout, "hello\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.status_id, 3)
        self.assertEqual(result.status_description, "Accepted")

    # Verify that non-accepted Judge0 statuses are returned as failed executions.
    def test_normalize_judge0_response_marks_failed_when_status_is_not_accepted(self):
        request = ExecutionRunRequest(code="while True: pass", language="python")
        response = {
            "stdout": None,
            "stderr": "",
            "compile_output": "",
            "message": None,
            "time": "1.00",
            "memory": 2048,
            "token": "abc",
            "status": {"id": 5, "description": "Time Limit Exceeded"},
        }

        result = normalize_judge0_response(response, request)

        self.assertFalse(result.passed)
        self.assertEqual(result.status_description, "Time Limit Exceeded")


if __name__ == "__main__":
    unittest.main()
