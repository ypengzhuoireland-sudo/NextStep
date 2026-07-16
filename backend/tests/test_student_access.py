import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas.sessions import UserProfile


class RequireStudentUserTest(unittest.TestCase):
    def test_missing_credentials_returns_401(self):
        from app.api.student_access import require_student_user

        with self.assertRaises(HTTPException) as context:
            require_student_user(None, db=object())

        self.assertEqual(context.exception.status_code, 401)

    @patch("app.api.student_access.get_user_from_access_token", return_value=None)
    def test_invalid_token_returns_401(self, _get_user):
        from app.api.student_access import require_student_user

        with self.assertRaises(HTTPException) as context:
            require_student_user(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid"),
                db=object(),
            )

        self.assertEqual(context.exception.status_code, 401)

    @patch("app.api.student_access.get_user_from_access_token")
    def test_teacher_token_returns_403(self, get_user):
        from app.api.student_access import require_student_user

        get_user.return_value = UserProfile(
            student_id="t1", username="teacher@example.test", name="Teacher", role="teacher"
        )

        with self.assertRaises(HTTPException) as context:
            require_student_user(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="teacher-token"),
                db=object(),
            )

        self.assertEqual(context.exception.status_code, 403)

    @patch("app.api.student_access.get_user_from_access_token")
    def test_student_token_returns_authenticated_student(self, get_user):
        from app.api.student_access import require_student_user

        student = UserProfile(
            student_id="s1", username="student@example.test", name="Student", role="student"
        )
        get_user.return_value = student

        result = require_student_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="student-token"),
            db=object(),
        )

        self.assertEqual(result, student)


if __name__ == "__main__":
    unittest.main()
