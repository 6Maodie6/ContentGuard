# ContentGuard

**基于 Python + FastAPI + pytest 的内容审核接口自动化测试项目**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-green.svg)](https://fastapi.tiangolo.com/)
[![pytest](https://img.shields.io/badge/pytest-Automation-orange.svg)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](https://coverage.readthedocs.io/)

## 1. 项目介绍

ContentGuard 是一个基于 Python 和 FastAPI 搭建的模拟内容审核系统，同时配套构建了 pytest 接口自动化测试体系。

项目模拟内容审核平台中的核心业务流程：用户提交内容后，系统根据预设规则进行风险分类；对于需要人工处理的内容，创建审核任务，并支持任务查询和人工审核。

项目重点不在于实现复杂的审核算法，而在于通过实际业务场景练习测试开发中的核心能力，包括：

- Python 接口自动化测试
- pytest 测试框架与参数化测试
- 等价类和边界值测试设计
- 单元测试与接口测试
- 任务状态迁移测试
- 新旧版本 Diff 测试
- Coverage.py 代码覆盖率分析
- 缺陷注入与测试有效性验证
- Allure 和 pytest-html 测试报告

## 2. 项目功能

### 2.1 内容自动审核

系统根据预设关键词模拟内容风险分类。

| 输入内容 | 审核结果 | 风险等级 |
|---|---|---|
| 普通内容 | pass | low |
| 低风险内容 | review | medium |
| 严重违规内容 | block | high |
| 诈骗内容（V2） | block | high |
| 同时包含严重违规和低风险关键词 | block | high |

### 2.2 审核任务管理

系统提供以下接口：

| 请求方式 | 接口 | 功能 |
|---|---|---|
| POST | `/api/v1/moderation/tasks` | 创建审核任务 |
| GET | `/api/v1/moderation/tasks/{task_id}` | 查询审核任务 |
| POST | `/api/v1/moderation/tasks/{task_id}/manual-review` | 人工审核 |

### 2.3 人工审核状态管理

任务状态包括：

- `pending`：等待人工审核
- `completed`：审核完成

状态流转：

```text
创建低风险审核任务
        |
        v
     pending
        |
        +---- 人工审核通过 ----> completed
        |
        +---- 人工审核拦截 ----> completed
        |
        +---- 非法审核结果 ----> 返回 400，保持 pending
        |
        +---- 重复审核 -------> 返回 409，拒绝操作
```

对于不存在的任务，接口返回 404。

## 3. 技术架构

### 3.1 技术栈

| 技术 | 用途 |
|---|---|
| Python 3.13 | 项目开发语言 |
| FastAPI | 搭建被测 API 服务 |
| Pydantic | 请求参数校验 |
| pytest | 自动化测试框架 |
| pytest.mark.parametrize | 参数化测试 |
| FastAPI TestClient | 模拟 HTTP 请求 |
| Coverage.py | 语句及分支覆盖率分析 |
| Allure | 自动化测试报告 |
| pytest-html | HTML 测试报告 |
| Git / GitHub | 版本管理和代码托管 |
| GitHub Actions | CI 自动化测试流程 |

### 3.2 项目结构

```text
ContentGuard/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── moderation.py
│   └── moderation_v2.py
│
├── tests/
│   ├── test_moderation.py
│   ├── test_moderation_unit.py
│   ├── test_moderation_v2_unit.py
│   ├── test_validation.py
│   ├── test_workflow.py
│   └── test_diff.py
│
├── data/
│   ├── moderation_cases.json
│   └── diff_cases.json
│
├── logs/
│
├── conftest.py
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```

### 3.3 核心模块说明

| 文件 | 功能 |
|---|---|
| `app/main.py` | FastAPI 应用、审核接口和任务状态管理 |
| `app/moderation.py` | V1 内容分类逻辑 |
| `app/moderation_v2.py` | V2 内容分类逻辑，新增诈骗关键词识别 |
| `tests/test_moderation.py` | 内容分类功能测试 |
| `tests/test_moderation_unit.py` | V1 分类函数单元测试 |
| `tests/test_moderation_v2_unit.py` | V2 分类函数单元测试 |
| `tests/test_validation.py` | 输入校验、边界值及异常场景测试 |
| `tests/test_workflow.py` | 人工审核任务状态迁移测试 |
| `tests/test_diff.py` | V1 与 V2 分类结果差异测试 |
| `data/` | 参数化测试数据 |
| `conftest.py` | pytest fixture 和测试客户端管理 |
| `pytest.ini` | pytest 测试配置 |

## 4. 环境准备

### 4.1 环境要求

- Python 3.13
- Git
- VS Code（推荐）
- Windows PowerShell 或其他支持 Python 的终端

### 4.2 克隆项目

```bash
git clone https://github.com/6Maodie6/ContentGuard.git

cd ContentGuard
```

### 4.3 创建虚拟环境

Windows PowerShell：

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4.4 安装依赖

```powershell
python -m pip install -r requirements.txt
```

检查 Python 环境：

```powershell
python --version
```

## 5. 项目运行

### 5.1 启动 FastAPI 服务

在项目根目录执行：

```powershell
uvicorn app.main:app --reload
```

服务启动后，可以访问：

```text
http://127.0.0.1:8000
```

FastAPI 交互式接口文档：

```text
http://127.0.0.1:8000/docs
```

### 5.2 执行全部自动化测试

```powershell
python -m pytest
```

显示详细测试结果：

```powershell
python -m pytest -v
```

只执行指定测试文件：

```powershell
python -m pytest tests/test_workflow.py -v
```

## 6. 自动化测试设计

项目围绕内容审核业务设计了多种测试场景。

### 6.1 功能测试

验证内容分类结果是否符合业务规则：

- 普通内容返回 pass
- 低风险内容返回 review
- 严重违规内容返回 block
- 严重违规优先于低风险
- V2 新增诈骗内容识别

### 6.2 等价类测试

将输入划分为有效和无效等价类。

| 输入类型 | 测试数据 | 预期结果 |
|---|---|---|
| 字符串 | 正常文本 | 正常处理 |
| 整数 | 123 | 拒绝输入 |
| 浮点数 | 12.5 | 拒绝输入 |
| 布尔值 | True | 拒绝输入 |
| 列表 | `["测试内容"]` | 拒绝输入 |
| 字典 | `{"text": "测试内容"}` | 拒绝输入 |
| 空值 | None | 请求校验失败 |

### 6.3 边界值测试

针对内容长度限制 1～500 字符设计边界值：

| 长度 | 预期结果 |
|---:|---|
| 0 | 拒绝输入 |
| 1 | 正常处理 |
| 2 | 正常处理 |
| 499 | 正常处理 |
| 500 | 正常处理 |
| 501 | 拒绝输入 |

### 6.4 单元测试

直接调用内容分类函数，验证函数自身的输入校验和异常处理逻辑。

重点覆盖：

- 非字符串输入
- 空字符串
- 超过最大长度
- 正常分类结果

### 6.5 状态迁移测试

验证任务在不同操作下的状态变化：

- 创建低风险任务后进入 pending
- 人工审核 pass 后进入 completed
- 人工审核 block 后进入 completed
- 已完成任务不能再次审核
- 非法审核决策不能改变原任务状态
- 不存在的任务不能进行人工审核

### 6.6 Diff 测试

通过比较 V1 和 V2 的内容分类结果，检查版本迭代带来的行为变化。

重点验证：

- 两个版本共有规则的行为一致性
- V2 新增诈骗识别规则
- 新版本是否引入非预期行为差异

## 7. 测试报告

项目支持使用 pytest-html 和 Allure 生成测试报告。

### 7.1 pytest-html 报告

执行：

```powershell
python -m pytest --html=report.html --self-contained-html
```

生成：

```text
report.html
```

### 7.2 Allure 报告

执行测试并生成 Allure 原始结果：

```powershell
python -m pytest --alluredir=allure-results
```

生成 HTML 报告：

```powershell
allure generate allure-results -o allure-report --clean
```

打开报告：

```powershell
allure open allure-report
```

以上命令需要已经安装 Allure Commandline，并确保 `allure` 命令可以在终端中使用。

## 8. 代码覆盖率分析

项目使用 Coverage.py 进行语句覆盖率和分支覆盖率分析。

### 8.1 安装 Coverage.py

```powershell
python -m pip install coverage
```

### 8.2 执行覆盖率统计

```powershell
python -m coverage erase

python -m coverage run --branch -m pytest

python -m coverage report -m
```

### 8.3 生成 HTML 覆盖率报告

```powershell
python -m coverage html
```

打开报告：

```powershell
start htmlcov/index.html
```

### 8.4 覆盖率结果

项目在当前测试范围内达到：

| 指标 | 最终结果 |
|---|---:|
| 语句覆盖率 | 100% |
| 分支覆盖率 | 100% |
| 未执行语句 | 0 |
| 未完全覆盖分支 | 0 |

通过覆盖率报告定位未执行代码和未覆盖分支，并针对输入校验、异常处理及接口业务路径补充测试用例。

**说明：100% 代码覆盖率不代表系统不存在 Bug，也不代表所有可能输入和业务场景均已验证。**

## 9. 缺陷注入实验

为验证自动化测试的缺陷检测能力，项目开展了三类缺陷注入实验。

### 实验一：关键词识别缺陷

**注入方式：**

将严重违规关键词判断：

```python
if "严重违规" in content:
```

故意修改为：

```python
if "严重违规错误" in content:
```

**验证目标：**

检查自动化测试能否发现严重违规内容未被正确识别的问题。

**预期结果：**

相关分类测试失败，恢复原代码后测试重新通过。

### 实验二：风险优先级缺陷

**注入方式：**

调换低风险和严重违规规则的判断顺序，使低风险规则先执行。

**验证目标：**

检查测试能否发现严重违规与低风险关键词同时出现时，系统错误返回 review 的问题。

**预期结果：**

严重违规优先级测试发现错误分类，恢复原顺序后测试通过。

### 实验三：任务状态转换缺陷

**注入方式：**

故意修改任务状态校验逻辑，使已经完成的任务仍然可以再次人工审核。

**验证目标：**

检查状态迁移测试能否发现非法状态转换及任务结果被覆盖的问题。

**预期结果：**

重复审核相关测试失败，恢复状态校验逻辑后测试通过。

### 实验总结

通过缺陷注入实验，验证自动化测试对以下问题的检测能力：

- 基础业务规则错误
- 多条规则之间的优先级错误
- 工作流状态管理错误

缺陷注入实验用于验证已设计测试的有效性，不代表测试能够发现所有类型的缺陷。

## 10. CI 自动化测试

项目配置 GitHub Actions 工作流：

```text
.github/workflows/tests.yml
```

用于在 GitHub Actions 环境中执行自动化测试。

工作流的实际执行状态可以在 GitHub 仓库的 Actions 页面查看：

https://github.com/6Maodie6/ContentGuard/actions

## 11. 项目实践收获

通过该项目，完成了以下实践：

1. 使用 FastAPI 搭建模拟内容审核服务。
2. 使用 pytest 构建接口自动化测试体系。
3. 使用参数化、等价类和边界值设计测试用例。
4. 使用 fixture 管理测试客户端和测试资源。
5. 实践人工审核任务状态迁移测试。
6. 实践 V1、V2 新旧版本 Diff 测试。
7. 使用 Coverage.py 分析语句和分支覆盖率。
8. 通过缺陷注入实验验证测试用例的缺陷检测能力。
9. 使用 Allure、pytest-html 生成自动化测试报告。
10. 使用 Git、GitHub 和 GitHub Actions 管理项目。

## 12. 后续改进方向

当前项目是一个用于测试开发实践的模拟系统，仍有进一步完善空间：

- **数据库持久化：** 将当前内存字典任务存储改为数据库存储。
- **真实审核能力：** 引入更丰富的审核规则或真实 AI 模型。
- **性能测试：** 使用 Locust 或 JMeter 对审核接口进行并发和压力测试。
- **并发测试：** 验证多个审核请求同时执行时的状态一致性。
- **测试体系完善：** 扩展接口异常、权限、安全性和兼容性测试。

## 13. License

本项目主要用于个人学习、测试开发实践及技术交流。

