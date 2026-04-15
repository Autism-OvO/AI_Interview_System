# AI 面试演练系统 — 项目架构图

```mermaid
graph TB
    subgraph Frontend["🖥️ 前端 (static/index.html)"]
        UI["Web UI<br/>Glassmorphism 风格"]
        Charts["Chart.js 图表<br/>雷达图 / 柱状图"]
        Recorder["浏览器录音<br/>MediaRecorder API"]
    end

    subgraph Backend["⚙️ Flask 后端 (app.py)"]
        direction TB
        API_Session["POST /api/start<br/>GET /api/question"]
        API_Answer["POST /api/answer<br/>POST /api/answer_audio"]
        API_Report["POST /api/report"]
        API_Model["GET /api/models<br/>POST /api/set_model"]
        API_KB["GET /api/kb/list<br/>POST /api/kb/add<br/>POST /api/kb/reload"]
        API_Trans["POST /api/transcribe"]
    end

    subgraph Core["🧠 面试核心引擎 (interview_core.py)"]
        SessionMgr["会话管理<br/>SESSIONS dict"]
        Evaluator["答案评估<br/>evaluate_answer()"]
        ReportGen["报告生成<br/>generate_report()"]
        subgraph RAG["📚 RAG 检索 (Retriever)"]
            Embedder["Embedding 模型<br/>bge-small-zh-v1.5"]
            FAISS["FAISS 向量索引<br/>faiss.index"]
            KBData["knowledge_base.json"]
        end
    end

    subgraph LLM["🤖 LLM 客户端 (llm_client.py)"]
        ModelMgr["模型管理<br/>多模型切换"]
        Scorer["多维度评分<br/>score_answer_with_llm()"]
        ReportLLM["报告生成<br/>generate_report_with_llm()"]
        PromptBuilder["Prompt 构建<br/>_build_prompt()"]
    end

    subgraph External["☁️ 外部 LLM 服务"]
        DeepSeek["DeepSeek Chat"]
        Doubao["豆包 Doubao"]
        GPT["GPT-4o-mini"]
    end

    QBank["📝 题库<br/>question_bank.py<br/>3 岗位 / 81 道题"]
    Transcriber["🎤 语音转录<br/>transcribe.py"]
    KeyConfig["🔑 key.py<br/>API Keys &amp; 模型配置"]
    CLI["💻 命令行演示<br/>run_demo.py"]

    WhisperLocal["Whisper 本地模型"]
    WhisperAPI["OpenAI Whisper API"]

    %% 前端 → 后端
    UI -->|HTTP REST| API_Session
    UI -->|HTTP REST| API_Answer
    UI -->|HTTP REST| API_Report
    UI -->|HTTP REST| API_Model
    UI -->|HTTP REST| API_KB
    Recorder -->|音频上传| API_Answer
    Recorder -->|音频上传| API_Trans

    %% 后端 → 核心
    API_Session --> SessionMgr
    API_Answer --> Evaluator
    API_Report --> ReportGen
    API_KB --> RAG

    %% 后端 → 转录
    API_Answer -->|语音回答| Transcriber
    API_Trans --> Transcriber

    %% 核心引擎内部
    SessionMgr --> QBank
    Evaluator --> Scorer
    Evaluator --> RAG
    ReportGen --> ReportLLM
    ReportGen --> RAG

    %% LLM 客户端
    Scorer --> PromptBuilder
    PromptBuilder --> ModelMgr
    ModelMgr --> External
    ReportLLM --> ModelMgr
    ModelMgr --> KeyConfig

    %% 转录
    Transcriber --> WhisperLocal
    Transcriber --> WhisperAPI
    Transcriber --> KeyConfig

    %% 后端 → LLM
    API_Model --> ModelMgr

    %% CLI
    CLI --> SessionMgr
    CLI --> Transcriber

    %% RAG 内部
    Embedder --> FAISS
    KBData --> Embedder

    %% 样式
    classDef frontend fill:#4f46e5,stroke:#6366f1,color:#fff
    classDef backend fill:#0891b2,stroke:#06b6d4,color:#fff
    classDef core fill:#7c3aed,stroke:#8b5cf6,color:#fff
    classDef llm fill:#059669,stroke:#10b981,color:#fff
    classDef external fill:#d97706,stroke:#f59e0b,color:#fff
    classDef util fill:#64748b,stroke:#94a3b8,color:#fff

    class UI,Charts,Recorder frontend
    class API_Session,API_Answer,API_Report,API_Model,API_KB,API_Trans backend
    class SessionMgr,Evaluator,ReportGen,Embedder,FAISS,KBData core
    class ModelMgr,Scorer,ReportLLM,PromptBuilder llm
    class DeepSeek,Doubao,GPT external
    class QBank,Transcriber,KeyConfig,CLI,WhisperLocal,WhisperAPI util
```

## 模块说明

| 层级 | 模块 | 职责 |
|------|------|------|
| **前端** | `static/index.html` | Glassmorphism 风格 Web UI，支持文本/语音输入，Chart.js 渲染评估图表 |
| **API 网关** | `app.py` | Flask 服务器，提供 12 个 REST 端点，路由请求到各模块 |
| **核心引擎** | `interview_core.py` | 会话管理、答案评估、RAG 知识库检索（bge-small-zh + FAISS） |
| **LLM 客户端** | `llm_client.py` | 多模型管理（DeepSeek/豆包/GPT），Prompt 构建，多维度评分与报告生成 |
| **辅助模块** | `question_bank.py` / `transcribe.py` / `key.py` | 题库（3 岗位 81 题）、语音转录（Whisper）、密钥配置 |
| **CLI** | `run_demo.py` | 命令行演示入口，支持麦克风录音 |
