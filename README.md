# AI 模拟面试与能力提升系统

基于 **RAG + LLM** 的智能面试演练平台，支持岗位化题库、多轮会话管理、语音识别作答、知识库检索增强评估和多维度面试报告生成。提供命令行与 Web 前端两种交互方式。

## 功能特性

- **岗位化题库** — 内置 Python 算法工程师、Java 后端工程师、Web 前端工程师三个岗位的面试题（含技术题、场景题、行为题）
- **RAG 知识检索** — 使用 sentence-transformers（`BAAI/bge-small-zh-v1.5`）生成文本向量，通过 FAISS 进行余弦相似度检索，为评估提供参考上下文；索引自动缓存，知识库未变时直接复用
- **LLM 深度评分** — 集成 DeepSeek / OpenAI 等大模型，从技术准确度、逻辑思维、沟通表达、问题解决四个维度打分并给出详细优劣势分析与改进建议；未配置 LLM 时回退为本地关键字启发式评分
- **语音识别作答** — 支持本地 Whisper 模型或 OpenAI Whisper API 两种语音转文本方式
- **语音表达评估（仅语音输入）** — 在语音转写后，将原始语音 + 转写文本送入 GPT 进行表达能力分析（语速、清晰度、自信度、感染力）
- **Web 前端** — 深色主题 UI，支持浏览器麦克风录音、实时作答、雷达图评分可视化、面试报告生成
- **知识库热更新** — 通过 API 动态添加知识条目并自动重建向量索引，无需重启服务
- **会话报告** — LLM 生成包含整体评价、各题详评与提升路径的面试报告

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置密钥

编辑 `key.py`，填入你的 API Key：

```python
key = {
    'ds': 'your-deepseek-api-key',     # DeepSeek API Key（用于 LLM 评分）
}
```

也可通过环境变量配置：

```powershell
$env:OPENAI_API_KEY = "sk-..."        # LLM 评分
$env:LLM_BASE_URL = "https://..."     # 自定义 LLM 端点（可选）
```

### 3. 运行

**命令行演示**（无需启动服务器）：

```bash
python run_demo.py
```

**Web 服务**：

```bash
python app.py
```

浏览器访问 `http://localhost:5000/` 即可使用前端页面。

## 语音识别

系统支持两种语音转文本后端：

| 后端               | 依赖                            | 说明                                                                |
| ------------------ | ------------------------------- | ------------------------------------------------------------------- |
| 本地 Whisper       | `whisper` + `ffmpeg`        | 离线可用，通过 `WHISPER_MODEL` 环境变量选择模型（默认 `small`） |
| OpenAI Whisper API | `openai` + `OPENAI_API_KEY` | 无需本地 GPU，调用远程 API                                          |

命令行模式下还可使用麦克风直接录音（需安装 `sounddevice` 和 `soundfile`）。

## 面试结果持久化（MySQL）

系统已支持将每次面试结果持久化到本地 MySQL，包含：

- 面试会话（候选人、岗位、总题数、完成状态、平均分）
- 每题评估记录（问题、首答、追问、追问回答、评分明细、RAG 片段）
- 会话报告（最终报告 JSON）

默认会在项目根目录自动读取 `db_config.json`，无需手动设置环境变量。

`db_config.json` 示例：

```json
{
    "mysql": {
        "enabled": 1,
        "host": "127.0.0.1",
        "port": 3306,
        "user": "ai_user",
        "password": "请改成你的MySQL密码",
        "database": "ai_interview",
        "charset": "utf8mb4"
    }
}
```

如需覆盖，也可继续使用环境变量：

```powershell
$env:DB_ENABLED = "1"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
$env:DB_USER = "ai_user"
$env:DB_PASSWORD = "你的密码"
$env:DB_NAME = "ai_interview"
```

Linux / WSL Bash 可使用：

```bash
export DB_ENABLED=1
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_USER=ai_user
export DB_PASSWORD='你的密码'
export DB_NAME=ai_interview
```

也可通过 `DB_CONFIG_FILE` 指定配置文件路径：

```bash
export DB_CONFIG_FILE=/path/to/your/db_config.json
```

服务启动后会自动建表：

- `interview_sessions`
- `interview_answers`
- `interview_reports`

## API 接口

| 方法         | 路径                             | 说明                                                                                                       |
| ------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `GET`      | `/api/positions`               | 获取所有可选岗位列表                                                                                       |
| `POST`     | `/api/start`                   | 创建面试会话，返回 `session_id` 与首题。Body: `{"role": "Java_Backend_Engineer", "candidate": "张三"}` |
| `GET`      | `/api/question?session_id=...` | 获取当前面试题                                                                                             |
| `POST`     | `/api/answer`                  | 提交文本回答，返回评估结果、RAG 片段与下一题。Body:`{"session_id": "...", "answer": "..."}`              |
| `POST`     | `/api/answer_audio`            | 提交音频回答（multipart form：`session_id` + `audio` 文件），自动转录后评估                            |
| `POST`     | `/api/transcribe`              | 单独语音转文本接口（上传 `audio` 文件）                                                                  |
| `GET/POST` | `/api/report`                  | 获取面试会话的综合报告。`session_id` 通过 query 参数或 JSON body 传入                                    |
| `GET`      | `/api/growth_curve`            | 获取候选人历史成长曲线。Query: `candidate`、`role`(可选)、`limit`(可选，默认20)                          |
| `GET`      | `/api/kb/list`                 | 查看知识库全部内容与统计                                                                                   |
| `POST`     | `/api/kb/add`                  | 添加知识条目并重建索引。Body:`{"role": "岗位名", "title": "标题", "text": "内容"}`                       |
| `POST`     | `/api/kb/reload`               | 手动触发知识库重新加载与索引重建                                                                           |

前端入口说明：

- 面试主页点击「成长曲线」按钮，会进入独立页面 `/growth`
- 成长曲线页面点击「查询曲线」后才会拉取并展示历史数据（非实时自动刷新）

`/api/answer_audio` 返回中新增字段：

- `speech_evaluation`: 语音表达评分对象，仅在语音输入接口中返回
- 字段包括：`speech_rate`、`clarity`、`confidence`、`expressiveness`、`overall`、`summary`、`suggestions`

## 项目结构

```
├── app.py                  # Flask Web 服务与 API 路由
├── interview_core.py       # 核心逻辑：Retriever 检索器、会话管理、评估与报告
├── llm_client.py           # LLM 客户端：多维评分 prompt 构建、JSON 解析、报告生成
├── question_bank.py        # 岗位化面试题库
├── transcribe.py           # 语音转文本（Whisper 本地 / OpenAI API）
├── run_demo.py             # 命令行交互式面试演示
├── key.py                  # API 密钥与 Embedding 配置（不应提交到公开仓库）
├── knowledge_base.json     # 知识库原始数据
├── requirements.txt        # Python 依赖
├── static/
│   └── index.html          # Web 前端页面（深色主题，含雷达图与录音功能）
├── vector_index/
│   └── faiss.index         # FAISS 向量索引缓存（自动生成）
└── tmp_audio/              # 上传音频临时存储目录
```

## 技术栈

- **后端**：Flask、NumPy
- **向量检索**：sentence-transformers（`BAAI/bge-small-zh-v1.5`）+ FAISS (faiss-cpu)
- **LLM**：OpenAI SDK（兼容 DeepSeek / Volcengine Ark 等 OpenAI 格式端点）
- **语音识别**：OpenAI Whisper（本地模型）/ Whisper API
- **前端**：原生 HTML/CSS/JS、Chart.js（雷达图）、Phosphor Icons
