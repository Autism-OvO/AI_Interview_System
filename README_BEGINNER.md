# AI 面试系统新手上手指南（零基础版）

> 这是一份给纯新手的说明文档，不会替换你现有的 README。

## 1. 你将完成什么

按这份文档做完后，你可以：

- 在本机创建 Python 运行环境
- 安装项目依赖
- 初始化 MySQL 数据库
- 配置模型 Key 与数据库连接
- 启动 Web 服务并访问页面

---

## 2. 前置准备

请先确认你有这些工具：

- WSL2（Windows 用户强烈建议）
- uv（推荐的 Python 环境与包管理工具）
- Python 3.10 或 3.11（建议 3.11）
- MySQL 8.x（建议）
- Git（可选，用于版本管理）

可用下面命令自检：

```bash
uv --version
python --version
mysql --version
```

如果 `python` 命令不存在，Linux 上可试：

```bash
python3 --version
```

### 2.1 Windows 用户：先用 WSL 再开发（推荐）

如果你是 Windows 用户，建议在 WSL Ubuntu 里完成全部开发，避免路径、权限和换行符问题。

先在 PowerShell 安装 WSL（只需一次）：

```powershell
wsl --install -d Ubuntu
```

重启后打开 Ubuntu 终端，在 WSL 里继续执行本文档的命令。

### 2.2 在 WSL / Linux 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

Windows PowerShell 也可安装 uv（如果你不用 WSL）：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

---

## 3. 进入项目目录

```bash
cd /home/chobits/AI_Interview_System
```

Windows PowerShell 请切到你的项目路径，例如：

```powershell
cd D:\AI_Interview_System
```

---

## 4. 使用 uv 创建并管理虚拟环境（推荐）

### WSL / Linux / macOS

```bash
uv venv --python 3.11
source .venv/bin/activate
```

### Windows PowerShell

```powershell
uv venv --python 3.11
.venv\Scripts\Activate.ps1
```

激活成功后，命令行前面通常会出现 `(.venv)`。

### 传统方式（不使用 uv 时兜底）

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## 5. 使用 uv 安装依赖

推荐命令（更快）：

```bash
uv pip install -r requirements.txt
```

如果你没有激活环境，也可以：

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

Windows 对应命令：

```powershell
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

### 传统 pip 方式（兜底）

```bash
pip install -r requirements.txt
```

如果下载很慢，可先升级 pip 再重试：

```bash
python -m pip install --upgrade pip
```

---

## 6. 初始化 MySQL（重点）

这个项目会把面试分数写进 MySQL。程序启动时会自动建表，但前提是：

- MySQL 服务已经启动
- 数据库已经存在
- 用户名密码正确

### 6.1 进入 MySQL

```bash
mysql -u root -p
```

输入 root 密码后，执行下面 SQL（可直接复制）：

```sql
CREATE DATABASE IF NOT EXISTS ai_interview
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'ai_user'@'localhost' IDENTIFIED BY '请改成你自己的密码';
CREATE USER IF NOT EXISTS 'ai_user'@'127.0.0.1' IDENTIFIED BY '请改成你自己的密码';

GRANT ALL PRIVILEGES ON ai_interview.* TO 'ai_user'@'localhost';
GRANT ALL PRIVILEGES ON ai_interview.* TO 'ai_user'@'127.0.0.1';

FLUSH PRIVILEGES;
```

可选验证：

```sql
USE ai_interview;
SHOW TABLES;
```

第一次启动项目前，`SHOW TABLES;` 可能为空，这是正常的。

### 6.2 配置数据库连接

编辑 `db_config.json`，改成你自己的密码：

```json
{
  "mysql": {
    "enabled": 1,
    "host": "127.0.0.1",
    "port": 3306,
    "user": "ai_user",
    "password": "你刚才设置的密码",
    "database": "ai_interview",
    "charset": "utf8mb4"
  }
}
```

说明：

- `enabled: 1` 表示开启数据库持久化
- 如果你暂时不想用 MySQL，可以改成 `enabled: 0`

---

## 7. 配置大模型 Key

项目新增了一个安全模板：`key_demo.py`（不含真实密钥）。

推荐按下面步骤配置：

### 7.1 从模板复制出本地配置

Linux / macOS:

```bash
cp key_demo.py key.py
```

Windows PowerShell:

```powershell
copy key_demo.py key.py
```

### 7.2 编辑 key.py 填入真实值

需要替换这些占位符：

- `your-deepseek-api-key`
- `your-volcengine-ark-api-key`
- `your-openai-api-key`
- `your-doubao-model-id`
- `your-thinking-model-id`

至少保证你正在使用的模型条目里 `api_key` 与 `model` 是有效的。

新手建议先保留一个模型先跑通（例如 deepseek），确认可用后再添加其他模型。

安全建议：

- `key.py` 不要上传到公开仓库
- `key_demo.py` 可以上传，它只用于示例
- 如果你曾经泄露过 key，请立即去对应平台重置（rotate）

---

## 8. 启动项目

```bash
python app.py
```

如果你希望全程用 uv，也可以：

```bash
uv run python app.py
```

看到类似下面输出说明启动成功：

- Running on http://127.0.0.1:5000
- 或 Running on http://0.0.0.0:5000

浏览器打开：

- http://127.0.0.1:5000/

---

## 9. 验证 MySQL 是否写入成功

完成一次面试后，回到 MySQL 执行：

```sql
USE ai_interview;
SHOW TABLES;
SELECT COUNT(*) FROM student_scores;
```

如果能看到 `student_scores` 表，且计数大于 0，说明持久化正常。

---

## 10. 常见报错与处理

### 10.1 `Author identity unknown`（Git 提交时报错）

这是 Git 没有配置用户名邮箱：

```bash
git config user.name "你的名字"
git config user.email "你的邮箱"
```

### 10.2 `DB_PASSWORD is empty, DB persistence disabled`

说明数据库密码为空。检查 `db_config.json` 的 `password`。

### 10.3 `DB init failed, persistence disabled`

常见原因：

- MySQL 没启动
- 用户名/密码错误
- 数据库不存在
- 账号没有权限

按第 6 节重新执行 SQL 初始化一般能解决。

### 10.4 `ModuleNotFoundError`

通常是依赖没装好或虚拟环境没激活：

```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

Windows 则使用 `.venv\Scripts\Activate.ps1`。

---

## 11. 给纯新手的建议

- 先跑通最小链路：启动服务 -> 打开网页 -> 完成一次问答
- 然后再折腾语音识别、模型切换、知识库扩展
- 每改一处配置就重启一次 `python app.py`，避免旧状态干扰

如果你愿意，我下一步可以再给你补一份“Windows 专用版一步一步截图式清单”。
