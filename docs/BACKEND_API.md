# NextStep 后端现有接口文档


## 1. 基础信息

### 服务信息

| 项 | 值 |
|---|---|
| 框架 | FastAPI |
| OpenAPI | `3.1.0` |
| API title | `FastAPI` |
| API version | `0.1.0` |
| 文档地址 | `/docs`、`/redoc` |
| OpenAPI JSON | `/openapi.json` |

### 路径前缀

当前后端接口分为两类：

- 鉴权接口：直接挂在 `/auth/*`
- 业务接口：挂在 `/api/*`

例如：

```http
POST /auth/login
GET /api/exercises
```

### 请求格式

```http
Content-Type: application/json
```

### 鉴权方式

需要登录的接口使用 Bearer Token：

```http
Authorization: Bearer <access_token>
```

OpenAPI 中标记需要鉴权的接口：

- `GET /auth/me`
- `DELETE /auth/me`
- `POST /auth/logout`
- `GET /api/dashboard/student`
- `GET /api/mastery/me`
- `GET /api/students/{student_id}/mastery`

未携带 Authorization header 时，当前后端返回示例：

```json
{
  "detail": "Missing Authorization header"
}
```

### 错误响应

FastAPI 参数校验失败时返回 `422`，格式为：

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

## 2. 接口总览

| 方法 | 路径 | 鉴权 | 成功状态码 | 说明 |
|---|---|---:|---:|---|
| `POST` | `/auth/login` | 否 | `200` | 用户登录 |
| `POST` | `/auth/register` | 否 | `201` | 用户注册 |
| `GET` | `/auth/me` | 是 | `200` | 获取当前用户信息 |
| `POST` | `/auth/refresh` | 否 | `200` | 刷新 access token |
| `POST` | `/auth/logout` | 是 | `200` | 退出登录 |
| `DELETE` | `/auth/me` | 是 | `200` | 删除当前账号（注销） |
| `GET` | `/api/dashboard/student` | 是 | `200` | 获取学生首页 dashboard |
| `GET` | `/api/dashboard/class-summary` | 否 | `200` | 获取教师端班级看板 |
| `GET` | `/api/exercises` | 否 | `200` | 查询题目列表 |
| `GET` | `/api/exercises/{exercise_id}` | 否 | `200` | 获取题目详情 |
| `GET` | `/api/kcs` | 否 | `200` | 查询知识点列表 |
| `GET` | `/api/kcs/{code}` | 否 | `200` | 获取知识点详情 |
| `GET` | `/api/mastery/me` | 是 | `200` | 获取当前登录学生 mastery |
| `GET` | `/api/students/{student_id}/mastery` | 是 | `200` | 获取指定学生 mastery |
| `GET` | `/` | 否 | `200` | 根路径 |

## 3. 鉴权接口

### 3.1 登录

```http
POST /auth/login
```

Request body:

```json
{
  "username": "demo",
  "password": "password123"
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |

Response `200`:

```json
{
  "student_id": "stu_001",
  "username": "demo",
  "name": "Demo Student",
  "role": "student",
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `student_id` | string | 是 | 学生 ID |
| `username` | string | 是 | 用户名 |
| `name` | string | 是 | 展示名 |
| `role` | string | 是 | 用户角色 |
| `access_token` | string | 是 | 访问 token |
| `refresh_token` | string | 是 | 刷新 token |
| `token` | string | 是 | 兼容字段，值通常等于 access token |
| `token_type` | string | 是 | token 类型 |
| `expires_in` | integer | 是 | access token 有效期，单位秒 |

### 3.2 注册

```http
POST /auth/register
```

Request body:

```json
{
  "username": "demo",
  "password": "password123",
  "name": "Demo Student"
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |
| `name` | string | 是 | 展示名 |

Response `201`: 同登录接口的 `LoginResponse`。

### 3.3 获取当前用户

```http
GET /auth/me
Authorization: Bearer <access_token>
```

Response `200`:

```json
{
  "student_id": "stu_001",
  "username": "demo",
  "name": "Demo Student",
  "role": "student"
}
```

### 3.4 刷新 Token

```http
POST /auth/refresh
```

Request body:

```json
{
  "refresh_token": "eyJ..."
}
```

Response `200`:

```json
{
  "access_token": "eyJ...",
  "token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3.5 退出登录

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

Request body 可为空，也可以传 refresh token：

```json
{
  "refresh_token": "eyJ..."
}
```

Response `200`:

```json
{
  "message": "Logged out"
}
```

### 3.6 删除当前账号（注销）

```http
DELETE /auth/me
Authorization: Bearer <access_token>
```

Response `200`:

```json
{
  "message": "Account deleted"
}
```

## 4. Dashboard

### 4.1 获取学生 Dashboard

```http
GET /api/dashboard/student
Authorization: Bearer <access_token>
```

Response `200`:

```json
{
  "student_name": "Demo Student",
  "active_goal": "Improve list traversal",
  "backend_status": "ok",
  "mastery_average": 0.68,
  "recommended_exercise_id": "ex_lists_012",
  "knowledge_components": [
    {
      "id": "lists",
      "name": "Lists",
      "mastery": 0.46
    }
  ],
  "exercises": [
    {
      "id": "ex_lists_012",
      "title": "Filter Passing Scores",
      "kc": "lists",
      "difficulty": "medium",
      "status": "published"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `student_name` | string | 是 | 学生展示名 |
| `active_goal` | string | 是 | 当前学习目标 |
| `backend_status` | string | 是 | 后端状态 |
| `mastery_average` | number | 是 | 平均掌握度 |
| `recommended_exercise_id` | string | 是 | 推荐题目 ID |
| `knowledge_components` | array | 是 | 简版知识点列表 |
| `exercises` | array | 是 | 简版题目列表 |

### 4.2 获取教师端班级看板

```http
GET /api/dashboard/class-summary?class_id=demo-python-101
```

Query:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `class_id` | string | 否 | 班级 ID，默认 `demo-python-101` |

Response `200`:

```json
{
  "classId": "demo-python-101",
  "updatedAt": "2026-06-09T10:30:00Z",
  "totals": {
    "students": 24,
    "averageMastery": 0.64,
    "submissions7d": 186,
    "hintRequests7d": 73,
    "atRiskCount": 5
  },
  "heatmap": [
    {
      "studentId": "stu_python_beginner_01",
      "displayName": "Demo Student",
      "kcCode": "lists",
      "kcName": "Lists",
      "mastery": 0.46
    }
  ],
  "riskStudents": [
    {
      "studentId": "stu_python_beginner_01",
      "displayName": "Demo Student",
      "averageMastery": 0.44,
      "failedAttempts7d": 9,
      "hintsUsed7d": 6,
      "weakestKc": "exceptions",
      "lastActiveAt": "2026-06-09T10:24:00Z"
    }
  ],
  "weakKcs": [
    {
      "kcCode": "exceptions",
      "kcName": "Exceptions",
      "averageMastery": 0.31,
      "affectedStudents": 12,
      "trend": -0.04
    }
  ],
  "recentSubmissions": [
    {
      "id": "sub_01",
      "studentId": "stu_python_beginner_01",
      "displayName": "Demo Student",
      "exerciseTitle": "Filter Passing Scores",
      "kcCode": "lists",
      "status": "passed",
      "passedCount": 4,
      "totalCount": 4,
      "runtimeMs": 38,
      "createdAt": "2026-06-09T10:24:00Z"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `classId` | string | 是 | 班级 ID |
| `updatedAt` | string | 是 | 更新时间 |
| `totals` | object | 是 | 班级统计汇总 |
| `heatmap` | array | 是 | 学生和知识点 mastery 热力图 |
| `riskStudents` | array | 是 | 低 mastery 学生列表 |
| `weakKcs` | array | 是 | 薄弱知识点列表 |
| `recentSubmissions` | array | 是 | 最近提交记录 |

## 5. Exercises

### 5.1 查询题目列表

```http
GET /api/exercises?kc=lists&difficulty=medium&status=published
```

Query:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `kc` | string | 否 | 知识点编码 |
| `difficulty` | string | 否 | 难度 |
| `status` | string | 否 | 题目状态 |

Response `200`:

```json
{
  "items": [
    {
      "id": "ex_lists_012",
      "title": "Filter Passing Scores",
      "difficulty": "medium",
      "primaryKc": "lists",
      "estimatedMinutes": 14,
      "status": "published"
    }
  ],
  "total": 1
}
```

### 5.2 获取题目详情

```http
GET /api/exercises/{exercise_id}
```

Path:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `exercise_id` | string | 是 | 题目 ID |

Response `200`:

```json
{
  "id": "ex_lists_012",
  "title": "Filter Passing Scores",
  "slug": "filter-passing-scores",
  "difficulty": "medium",
  "estimatedMinutes": 14,
  "prompt": "Write a function passing_scores(scores)...",
  "goal": "Practice list traversal and conditionals.",
  "constraints": [
    "Return a list, not printed output."
  ],
  "examples": [
    {
      "input": "passing_scores([88, 42, 60])",
      "output": "[88, 60]",
      "explanation": "60 is included."
    }
  ],
  "starterCode": "def passing_scores(scores):\n    return []\n",
  "kcTags": [
    {
      "code": "lists",
      "name": "Lists",
      "description": "List creation, indexing, traversal.",
      "mastery": 0.46,
      "trend": -0.06,
      "state": "needs_practice"
    }
  ],
  "recommendation": {
    "strategy": "lowest_mastery_with_difficulty_match",
    "reason": "Lists mastery is below the target threshold.",
    "confidence": 0.86
  }
}
```

注意：该接口响应字段混用了 snake_case 和 camelCase 之外的业务命名；OpenAPI 中明确为 `estimatedMinutes`、`starterCode`、`kcTags`。

## 6. Knowledge Components

### 6.1 查询知识点列表

```http
GET /api/kcs
```

Response `200`:

```json
{
  "items": [
    {
      "code": "lists",
      "name": "Lists",
      "description": "List creation, indexing, traversal.",
      "exerciseCount": 4
    }
  ],
  "total": 1
}
```

### 6.2 获取知识点详情

```http
GET /api/kcs/{code}
```

Path:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `code` | string | 是 | 知识点编码 |

Response `200`:

```json
{
  "code": "lists",
  "name": "Lists",
  "description": "List creation, indexing, traversal.",
  "exerciseCount": 4,
  "exerciseIds": [
    "ex_lists_012"
  ]
}
```

## 7. Mastery

### 7.1 获取当前登录学生 Mastery

```http
GET /api/mastery/me
Authorization: Bearer <access_token>
```

Response `200`:

```json
{
  "studentId": "stu_001",
  "updatedAt": "2026-06-09T10:30:00Z",
  "items": [
    {
      "code": "lists",
      "name": "Lists",
      "description": "List creation, indexing, traversal.",
      "mastery": 0.46,
      "trend": -0.06,
      "state": "needs_practice"
    }
  ]
}
```

### 7.2 获取指定学生 Mastery (教师)

```http
GET /api/students/{student_id}/mastery
Authorization: Bearer <access_token>
```

Path:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `student_id` | string | 是 | 学生 ID |

Response `200`: 同 `GET /api/mastery/me`。

## 8. Root

### 8.1 根路径

```http
GET /
```

OpenAPI 标记该接口返回 `200`，未定义明确 response schema。

## 9. 当前后端没有注册的前端接口

下面这些接口在当前前端代码中有调用或曾在旧文档中出现，但当前后端 OpenAPI 没有注册：

| 方法 | 路径 | 影响 |
|---|---|---|
| `POST` | `/api/sessions` | 前端创建练习 session 不可用 |
| `GET` | `/api/session/current-exercise` | 学生练习首屏接口不可用 |
| `POST` | `/api/executions/run` | 运行代码接口不可用 |
| `POST` | `/api/submissions` | 提交代码接口不可用 |
| `POST` | `/api/hints` | 请求提示接口不可用 |
| `POST` | `/api/recommendations/next` | 下一题推荐接口不可用 |

如果前端要切到真实后端，需要么按当前后端接口改前端调用，要么在后端补齐以上接口。

