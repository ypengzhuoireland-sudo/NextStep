# NextStep API Contract

## 0. Student Auth Mock

The current project is frontend-only. Student login is implemented in
`frontend/src/api/studentAuth.ts` with browser `localStorage`; no backend or
database is required.

Local storage keys:

- `nextstep_student_token`
- `nextstep_student_user`
- `nextstep_student_accounts` (registered accounts in this frontend mock)

Demo student:

```json
{
  "email": "student@nextstep.test",
  "password": "demo1234"
}
```

Frontend API functions:

- `loginStudent({ email, password })`
- `registerStudent({ name, email, password })`
- `getStudentMe()`
- `logoutStudent()`

Future backend contract can keep the same response shape:

### POST /api/auth/student/login

Request:

```json
{
  "email": "student@nextstep.test",
  "password": "demo1234"
}
```

Response:

```json
{
  "token": "student_stu_python_beginner_01",
  "user": {
    "id": "stu_python_beginner_01",
    "name": "Python Beginner",
    "email": "student@nextstep.test",
    "avatarInitials": "PB"
  }
}
```

### POST /api/auth/student/register

Request:

```json
{
  "name": "Python Beginner",
  "email": "student2@nextstep.test",
  "password": "demo1234"
}
```

Response:

```json
{
  "token": "student_stu_local_1780000000000",
  "user": {
    "id": "stu_local_1780000000000",
    "name": "Python Beginner",
    "email": "student2@nextstep.test",
    "avatarInitials": "PB"
  }
}
```

### GET /api/auth/student/me

Request header:

```txt
Authorization: Bearer student_stu_python_beginner_01
```

Response:

```json
{
  "user": {
    "id": "stu_python_beginner_01",
    "name": "Python Beginner",
    "email": "student@nextstep.test",
    "avatarInitials": "PB"
  }
}
```

本文档定义前端需要的 FastAPI REST 接口。当前前端使用 mock 数据实现，后端接入时按以下 JSON 契约返回即可。

## 基础约定

- Base URL: `/api`
- Content-Type: `application/json`
- 时间字段使用 ISO 8601。
- mastery probability 使用 `0` 到 `1` 的小数。
- 前端默认学生端为匿名 session，后续可接登录系统。

## 数据类型

### KnowledgeComponent

```json
{
  "code": "lists",
  "name": "Lists",
  "description": "List creation, indexing, traversal.",
  "mastery": 0.46,
  "trend": -0.06,
  "state": "needs_practice"
}
```

`state`: `needs_practice | almost_there | mastered`

### Exercise

```json
{
  "id": "ex_lists_012",
  "title": "Filter Passing Scores",
  "slug": "filter-passing-scores",
  "difficulty": "medium",
  "estimatedMinutes": 14,
  "prompt": "Write a function passing_scores(scores)...",
  "goal": "Practice list traversal and conditionals.",
  "constraints": ["Return a list, not printed output."],
  "examples": [
    {
      "input": "passing_scores([88, 42, 60])",
      "output": "[88, 60]",
      "explanation": "60 is included."
    }
  ],
  "starterCode": "def passing_scores(scores):\n    return []\n",
  "kcTags": [],
  "recommendation": {
    "strategy": "lowest_mastery_with_difficulty_match",
    "reason": "Lists mastery is below the target threshold.",
    "confidence": 0.86
  }
}
```

`difficulty`: `easy | medium | hard`

## 1. Create Session

`POST /api/sessions`

创建匿名或测试 session，并分配实验组。

Request:

```json
{
  "display_name": "Demo Student",
  "preferred_group": "adaptive"
}
```

Response:

```json
{
  "session_id": "ses_01JZ...",
  "student_id": "stu_01JZ...",
  "experiment_group": "adaptive"
}
```

## 2. Current Exercise

`GET /api/session/current-exercise?session_id=ses_01JZ...`

返回当前推荐题、学生 mastery、学习路径和最近提交结果。

Response:

```json
{
  "sessionId": "ses_01JZ...",
  "studentId": "stu_01JZ...",
  "experimentGroup": "adaptive",
  "exercise": {},
  "masteryProfile": [],
  "learningPath": [],
  "dashboardSeries": [],
  "latestResult": null,
  "hintMessages": []
}
```

## 3. Query Exercises

`GET /api/exercises?kc=lists&difficulty=medium&status=published`

Response:

```json
{
  "items": [
    {
      "id": "ex_lists_012",
      "title": "Filter Passing Scores",
      "difficulty": "medium",
      "primary_kc": "lists",
      "estimated_minutes": 14
    }
  ],
  "total": 1
}
```

## 4. Exercise Detail

`GET /api/exercises/{exercise_id}`

Response: `Exercise`

## 5. Run Code

`POST /api/executions/run`

只运行公开测试，不写入最终提交记录，可用于编辑器快速验证。

Request:

```json
{
  "session_id": "ses_01JZ...",
  "exercise_id": "ex_lists_012",
  "language": "python",
  "code": "def passing_scores(scores):\n    return scores\n"
}
```

Response:

```json
{
  "id": "run_01JZ...",
  "status": "failed",
  "summary": "2 of 4 tests passed.",
  "errorType": "failed_tests",
  "runtimeMs": 43,
  "memoryMb": 18.4,
  "passedCount": 2,
  "totalCount": 4,
  "stdout": "Running pytest harness...",
  "stderr": "AssertionError...",
  "testCases": [
    {
      "id": "case_1",
      "label": "Boundary score",
      "input": "[88, 60]",
      "expected": "[88, 60]",
      "actual": "[88]",
      "hidden": false,
      "passed": false,
      "runtimeMs": 11
    }
  ],
  "masteryDelta": []
}
```

`status`: `running | passed | failed | error`

`errorType`: `syntax_error | runtime_error | failed_tests | timeout`

## 6. Submit Code

`POST /api/submissions`

提交代码、运行测试、保存 submission log、更新 mastery。

Request:

```json
{
  "session_id": "ses_01JZ...",
  "student_id": "stu_01JZ...",
  "exercise_id": "ex_lists_012",
  "language": "python",
  "code": "def passing_scores(scores):\n    return [s for s in scores if s >= 60]\n"
}
```

Response:

```json
{
  "submission": {
    "id": "sub_01JZ...",
    "status": "passed",
    "correct": true,
    "attempt_count": 3,
    "created_at": "2026-06-05T13:40:00Z"
  },
  "result": {
    "id": "sub_01JZ...",
    "status": "passed",
    "summary": "All tests passed.",
    "runtimeMs": 38,
    "memoryMb": 18.1,
    "passedCount": 4,
    "totalCount": 4,
    "stdout": "case_1 passed",
    "stderr": "",
    "testCases": [],
    "masteryDelta": [
      {
        "kcCode": "lists",
        "before": 0.49,
        "after": 0.57
      }
    ]
  },
  "masteryProfile": []
}
```

## 7. Request Hint

`POST /api/hints`

根据题目、最近提交、错误摘要和 mastery profile 生成分层 hint。

Request:

```json
{
  "session_id": "ses_01JZ...",
  "student_id": "stu_01JZ...",
  "exercise_id": "ex_lists_012",
  "latest_submission_id": "sub_01JZ...",
  "requested_hint_level": 2
}
```

Response:

```json
{
  "id": "hint_01JZ...",
  "role": "assistant",
  "level": 2,
  "title": "Place the branch inside the loop",
  "text": "Inside for score in scores, check whether the current score passes.",
  "kcCode": "lists",
  "createdAt": "2026-06-05T13:42:00Z",
  "avoid_full_solution": true
}
```

## 8. Next Recommendation

`POST /api/recommendations/next`

Request:

```json
{
  "session_id": "ses_01JZ...",
  "student_id": "stu_01JZ...",
  "strategy": "adaptive"
}
```

Response:

```json
{
  "exercise": {},
  "reason": "Recommended because list_operations mastery is 0.39 below threshold 0.75.",
  "strategy": "lowest_mastery_with_difficulty_match",
  "confidence": 0.82
}
```

## 9. Student Mastery

`GET /api/students/{student_id}/mastery`

Response:

```json
{
  "student_id": "stu_01JZ...",
  "updated_at": "2026-06-05T13:45:00Z",
  "items": []
}
```

## 10. Class Dashboard

`GET /api/dashboard/class-summary?class_id=demo`

Response:

```json
{
  "class_id": "demo",
  "heatmap": [
    {
      "student_id": "stu_01JZ...",
      "kc_code": "lists",
      "mastery": 0.57
    }
  ],
  "risk_students": [
    {
      "student_id": "stu_01JZ...",
      "display_name": "Demo Student",
      "average_mastery": 0.44,
      "failed_attempts_7d": 9
    }
  ],
  "weak_kcs": [
    {
      "kc_code": "exceptions",
      "average_mastery": 0.31,
      "affected_students": 12
    }
  ]
}
```

## 11. Evaluation Export

`GET /api/evaluation/export?format=json`

用于导出 adaptive vs baseline 实验日志。

Response:

```json
{
  "format": "json",
  "generated_at": "2026-06-05T13:50:00Z",
  "records": []
}
```

## 前端接入位置

真实后端完成后，替换：

- `frontend/src/api/tutor.ts`
- `frontend/src/api/client.ts` 中的 `VITE_API_BASE_URL`

建议保留 mock API 作为 demo fallback，可通过 `VITE_USE_MOCK=true` 控制。
