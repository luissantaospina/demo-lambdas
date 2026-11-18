# ⚡ demo-lambdas

> 🚀 Four hands-on demos of the newest **AWS Lambda** capabilities: Durable Functions, Managed Instances, MicroVMs and Web Functions.

## 🧩 What's inside

| | Folder | Demo | Runtime |
|---|---|---|---|
| 🔁 | [`durable_function/`](durable_function) | Payment flow: checkpointed steps, human approval via callback, exponential retries | Python |
| 🖥️ | [`managed_intance/`](managed_intance) | Cold vs. warm start, `/tmp` persistence and instance info | Python |
| 🧊 | [`microvm/`](microvm) | FastAPI movements API running in a Lambda MicroVM container | Python + Docker |
| 🌐 | [`web_function/`](web_function) | Plain HTTP server with an HTML home and an SSE stream | Node.js (ESM) |

## 🛠️ Requirements

- 🐍 Python 3.11+ · 🟢 Node.js 18+ · ☁️ AWS account · 🐳 Docker (MicroVM)
- `pip install -r requirements.txt`

## ▶️ Try them

### 🔁 Durable function
Invoke with:
```json
{ "payment_id": "pay-001", "amount": 100 }
```
Flow: **validate** → **wait for approval** (callback, 5 min timeout) → **capture funds** (4 attempts, 2s backoff ×2).
Resume the callback with [`approved-notification.json`](durable_function/approved-notification.json) ✅ or [`rejected-notification.json`](durable_function/rejected-notification.json) ❌.

### 🖥️ Managed instance
Invoke the handler several times and watch `conteo_invocaciones_en_esta_instancia` grow and the `/tmp` file persist 🔥.

### 🧊 MicroVM
```bash
pip install -r microvm/requirements.txt
python microvm/app.py          # http://localhost:8080
```
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check 💚 |
| `GET` | `/movements` | List movements 📄 |
| `POST` | `/movements` | Create a movement ➕ |

Image: `microvm/Dockerfile` (base `lambda/microvms:al2023-minimal`). Ready-to-upload bundle: `microvm-bundle.zip` 📦.

### 🌐 Web function
```bash
AWS_LAMBDA_HTTP_ENDPOINT=127.0.0.1:8080 node web_function/index.js
```
- `/` → home page 🏠 · `/stream` → 5 SSE messages, one per second 📡 · anything else → `404`
- Ready-to-upload bundle: `web-bundle.zip` 📦

## 🔗 Links
Each folder has an `important-links.txt` with the official docs, blog posts and SDKs 📚.
