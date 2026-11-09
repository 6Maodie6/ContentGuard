# ContentGuard - 内容审核接口自动化测试项目

## 1. 项目介绍

ContentGuard 是一个基于 Python 和 FastAPI 构建的模拟内容审核系统，主要用于实践接口自动化测试、测试数据驱动、Diff 差异测试以及持续集成。

项目模拟内容审核业务场景，实现内容提交、风险分类、审核任务查询和人工审核等功能，并使用 pytest 构建自动化测试体系，对接口功能、输入校验、业务流程和新旧规则差异进行验证。

本项目以测试开发岗位的实际工作能力为导向，重点实践被测服务搭建、自动化测试框架设计、测试数据管理、测试报告和 CI 流程。

> 说明：本项目为个人学习和测试实践项目，审核规则采用模拟关键词判断，不代表真实内容安全审核策略。

## 2. 技术栈

| 技术 | 用途 |
|---|---|
| Python | 项目主要开发语言 |
| FastAPI | 搭建被测内容审核 API 服务 |
| pytest | 自动化测试框架 |
| TestClient / httpx | 接口测试客户端 |
| Pydantic | 请求参数校验 |
| JSON | 测试数据管理 |
| pytest.mark.parametrize | 参数化测试 |
| pytest-html | HTML 测试报告 |
| Allure | 测试结果收集与报告 |
| Git / GitHub | 版本管理和代码托管 |
| GitHub Actions | 持续集成与自动化测试 |

## 3. 项目功能

### 3.1 内容审核

根据模拟审核规则对提交内容进行分类：

| 输入场景 | 审核结果 | 风险等级 |
|---|---|---|
| 普通内容 | pass | low |
| 低风险内容 | review | medium |
| 严重违规内容 | block | high |
| 同时包含低风险和严重违规 | block | high |

其中，严重违规规则具有更高优先级。

### 3.2 审核任务管理

实现以下 API：

| 请求方式 | 接口 | 功能 |
|---|---|---|
| POST | `/api/v1/moderation/tasks` | 创建审核任务 |
| GET | `/api/v1/moderation/tasks/{task_id}` | 查询审核任务 |
| POST | `/api/v1/moderation/tasks/{task_id}/manual-review` | 人工审核 |

主要业务规则：

- 审核内容必须为字符串。
- 内容长度限制为 1～500 个字符。
- 低风险内容进入待人工审核状态。
- 人工审核结果只能为 pass 或 block。
- 已完成的任务不能重复审核。
- 不存在的任务返回 404。

## 4. 自动化测试设计

项目使用 pytest 对内容审核服务进行自动化测试，主要覆盖以下场景：

### 4.1 功能测试

- 普通内容审核。
- 低风险内容审核。
- 严重违规内容审核。
- 多种风险关键词同时出现时的优先级判断。

### 4.2 参数校验测试

- 空字符串校验。
- 非字符串输入校验。
- 内容长度超过 500 个字符。
- 内容长度恰好为 500 个字符。
- 查询不存在的审核任务。

### 4.3 业务流程测试

- 创建待人工审核任务。
- 查询审核任务。
- 人工审核通过或拦截。
- 验证审核后的任务状态。
- 验证已完成任务不能重复审核。
- 验证非法人工审核结果。

### 4.4 数据驱动测试

将测试输入和预期结果保存在 JSON 文件中，使用 `pytest.mark.parametrize` 实现多组测试数据复用，降低重复代码，提高测试用例维护效率。

### 4.5 Diff 差异测试

分别使用旧版 V1 和新版 V2 审核规则处理相同输入，对比两个版本的审核结果。

通过预期差异数据判断：

- 原有规则是否保持一致。
- 新增规则是否产生预期变化。
- 是否出现非预期的结果变化。

## 5. 项目结构

```text
ContentGuard/
├── .github/
│   └── workflows/
│       └── tests.yml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── moderation.py
│   └── moderation_v2.py
├── tests/
│   ├── test_moderation.py
│   ├── test_validation.py
│   ├── test_workflow.py
│   └── test_diff.py
├── data/
│   ├── moderation_cases.json
│   └── diff_cases.json
├── logs/
├── conftest.py
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```

## 6. 环境准备

建议使用 Python 3.13。

克隆项目：

```bash
git clone https://github.com/你的GitHub用户名/ContentGuard.git
cd ContentGuard
```

创建虚拟环境：

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

## 7. 运行项目

启动 FastAPI 服务：

```bash
uvicorn app.main:app --reload
```

服务启动后，可以访问：

```text
http://127.0.0.1:8000/docs
```

通过 FastAPI Swagger UI 查看和调试接口。

## 8. 执行自动化测试

运行全部测试：

```bash
python -m pytest -v
```

运行指定测试文件：

```bash
python -m pytest tests/test_moderation.py -v
```

生成 pytest-html 报告：

```bash
python -m pytest --html=report.html --self-contained-html
```

生成 Allure 原始结果：

```bash
python -m pytest --alluredir=allure-results
```

生成并打开 Allure HTML 报告：

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

## 9. 持续集成（CI）

项目使用 GitHub Actions 实现持续集成。

工作流配置位于：

```text
.github/workflows/tests.yml
```

当代码推送到 main 分支或针对 main 分支创建 Pull Request 时，GitHub Actions 自动执行：

1. 获取仓库代码。
2. 配置 Python 运行环境。
3. 安装项目依赖。
4. 执行 pytest 自动化测试。
5. 根据测试结果判断工作流成功或失败。

通过 CI 流程验证代码变更，减少回归问题，提高项目交付质量。

## 10. 当前项目特点

- 使用 FastAPI 构建可测试的模拟业务服务。
- 使用 pytest 实现分层接口自动化测试。
- 使用 JSON 和参数化实现测试数据驱动。
- 使用 Diff 测试验证新旧规则变化。
- 使用 Allure 和 pytest-html 生成测试报告。
- 使用 GitHub Actions 自动执行回归测试。

## 11. 后续优化方向

- 将函数级 Diff 测试升级为接口级 Diff 测试。
- 引入数据库，实现审核任务持久化。
- 增加测试覆盖率统计和白盒测试。
- 引入 Locust 或 JMeter 开展性能测试。
- 探索 AI 内容审核模型的准确性、鲁棒性和一致性测试。

## 12. 项目说明

本项目为个人学习实践项目，重点在于理解接口自动化测试、测试设计、测试数据管理、差异测试和持续集成的基本方法。