# NextStep Dev Environment

Before running the backend, configure the API keys in:

```text
NextStep-dev/backend/.env
```

Required variables:

```env
JUDGE0_API_KEY=your_judge0_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

`JUDGE0_API_KEY` is required when `CODE_RUNNER_MODE=judge0`.

`OPENAI_API_KEY` is required for AI assistant and LLM-powered features.

Do not commit real API keys to the repository. Keep real secrets only in your local `.env` file.
