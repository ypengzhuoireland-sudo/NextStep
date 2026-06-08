# AI Programming Tutor Frontend Design

## 1. 页面结构

前端采用单页练习工作台，默认深色主题，视觉参考 Linear、Vercel、OpenAI、Cursor、LeetCode 的产品界面，而不是传统后台管理系统。

主页面：`PracticePage`

- 顶部：当前 session、实验组、学生视图状态。
- 左侧：当前练习题、KC 标签、难度、AI 推荐原因。
- 中间：Monaco Python Editor、运行按钮、提交按钮、编辑器工具栏。
- 右侧：AI Hint Panel、Mastery Progress、弱项 KC、推荐学习路径。
- 底部：Test Cases、Runtime Result、Error Message、Execution Status、学习状态图表。

布局在桌面端为三列工作台，在中小屏自动堆叠，保证编辑器和结果区优先可读。

## 2. React 组件拆分

```txt
src/
├── api/
│   ├── client.ts
│   └── tutor.ts
├── components/
│   ├── common/
│   │   ├── EmptyState.tsx
│   │   ├── LoadingScreen.tsx
│   │   └── StatPill.tsx
│   ├── dashboard/
│   │   ├── LearningAnalytics.tsx
│   │   └── SessionHeader.tsx
│   ├── exercise/
│   │   ├── CodeEditor.tsx
│   │   ├── ExercisePanel.tsx
│   │   ├── HintPanel.tsx
│   │   └── SubmitResultPanel.tsx
│   ├── mastery/
│   │   ├── LearningPath.tsx
│   │   ├── MasteryHeatmap.tsx
│   │   ├── MasteryRing.tsx
│   │   └── MasteryWidget.tsx
│   └── ui/
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── progress.tsx
│       ├── skeleton.tsx
│       ├── tabs.tsx
│       └── tooltip.tsx
├── data/mockTutorData.ts
├── hooks/usePracticeSession.ts
├── pages/PracticePage.tsx
├── types/tutor.ts
└── utils/formatters.ts
```

## 3. 核心组件职责

| Component | 职责 |
| --- | --- |
| `PracticePage` | 组合主练习页，管理页面布局和 hook 数据流。 |
| `SessionHeader` | 展示产品名称、学生 ID、session ID、实验组。 |
| `ExercisePanel` | 展示题目、样例、约束、KC 标签、推荐原因。 |
| `CodeEditor` | Monaco Python 编辑器、Run Code、Submit、Reset。 |
| `HintPanel` | ChatGPT 风格分层提示气泡，支持 L1/L2/L3 hint 请求。 |
| `MasteryWidget` | Progress ring、KC mastery heatmap、弱项 KC 列表。 |
| `LearningPath` | 展示当前推荐路径、后续练习和锁定状态。 |
| `SubmitResultPanel` | 测试用例、terminal 输出、错误信息、mastery delta。 |
| `LearningAnalytics` | Recharts 展示 mastery、attempts、hint usage。 |
| `usePracticeSession` | 加载 session、运行代码、提交代码、请求 hint、更新本地 mastery。 |

## 4. UI 风格原则

- 深色背景优先，叠加半透明玻璃面板和低饱和蓝紫环境光。
- 卡片圆角控制在 8px，界面保持 SaaS 产品的精密感。
- Monaco 编辑器是核心工作区，不做营销页式布局。
- Mastery 使用 progress ring，KC 使用 heatmap。
- Hint 使用聊天气泡，错误输出使用 terminal 风格。
- loading 使用 skeleton，未运行代码时使用优雅空状态。
- 所有主要动作具有 hover、disabled、loading 状态。

## 5. 当前实现说明

当前前端使用 mock API 跑通完整交互：

- 页面加载当前推荐题。
- Run Code 返回模拟测试结果。
- Submit 根据代码中是否包含 `.append(` 和 `>= 60` 返回 passed/failed。
- 请求 hint 会追加分层 AI 提示消息。
- 提交后会在前端模拟更新 mastery delta。

后端完成后，只需要替换 `src/api/tutor.ts` 中的 mock 方法为真实 REST 请求。
