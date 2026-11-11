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


## 3.3工程化与持续集成

项目在自动化测试基础上，实践了基础测试工程化流程。

### 1. 测试报告

- 使用 pytest-html 生成独立 HTML 测试报告。
- 实践 Allure pytest 插件及测试结果收集。
- 通过报告查看测试执行情况和失败用例。

### 2. 持续集成

使用 GitHub Actions 配置自动化测试工作流，主要包括：

1. 检出 GitHub 仓库代码。
2. 配置 Python 环境。
3. 安装项目依赖。
4. 执行 pytest 自动化测试。
5. 根据工作流配置生成或上传测试结果。

### 3. 版本管理

使用 Git 管理项目代码和版本变更，为测试代码维护、功能迭代及版本回归提供基础支持。

注：CI 工作流的实际执行状态和报告上传情况，以 GitHub Actions 运行记录为准。


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

## 7. 性能测试实践

使用 Locust 对 ContentGuard 内容审核服务开展接口负载测试、并发测试和稳定性观察。

### 1. 测试场景

除单接口压测外，设计了完整的审核业务链路：

1. 创建审核任务
2. 查询审核任务
3. 执行人工审核
4. 再次查询任务，验证最终状态

通过多个接口组合模拟实际业务操作，观察系统在持续请求下的响应表现。

### 2. 多轮并发测试

使用不同并发用户数开展测试：

| 测试轮次 | 并发用户数 | Spawn Rate |
|---|---:|---:|
| 第一轮 | 10 | 2 users/s |
| 第二轮 | 30 | 5 users/s |
| 第三轮 | 100 | 10 users/s |
| 第四轮 | 200 | 20 users/s |
| 稳定性测试 | 100 | 10 users/s |

已记录轮次的请求失败数均为 0。另进行了约 10 分钟的持续运行观察，用于观察服务响应和资源变化。

### 3. 完整业务链路压测结果

在本机环境下，使用 Locust 进行两轮完整业务链路压测。

测试条件：50 用户、5 users/s、持续 3 分钟。

| 性能指标 | 第一次 | 第二次 |
|---|---:|---:|
| HTTP 请求数 | 17,504 | 17,607 |
| 失败请求数 | 0 | 0 |
| 平均响应时间 | 1.22 ms | 1.21 ms |
| P95 | 2 ms | 2 ms |
| P99 | 3 ms | 3 ms |
| 平均 RPS | 97.24 | 97.82 |

### 4. 测试结论

- 两轮测试均未记录到失败请求。
- 两轮平均响应时间和 P95、P99 指标接近。
- 在当前测试条件下，接口表现相对稳定。
- 通过多接口业务链路验证，不仅关注单个接口，也关注完整业务流程。

**注意：** 以上数据来自本机模拟测试环境，不代表生产环境容量或线上 SLA。一个完整业务流程包含多个 HTTP 请求，HTTP RPS 不等于完整业务流程每秒完成数。

## 8. 性能分析与资源监控

为了进一步分析系统性能瓶颈，使用 Python 自带的 `cProfile` 对内容审核函数进行性能分析，并结合进程资源监控观察服务运行情况。

### 1. cProfile 函数性能分析

使用 `cProfile` 对 `classify_content` 函数进行性能分析。

实验中累计调用该函数 100,000 次，记录结果：

| 指标 | 实测结果 |
|---|---:|
| 函数调用次数 | 100,000 |
| 函数自身累计耗时（tottime） | 约 0.032 秒 |
| 累计耗时（cumtime） | 约 0.047 秒 |

通过分析函数调用次数和耗时，理解函数级性能分析的基本方法，为后续定位潜在性能瓶颈提供依据。

### 2. 资源监控

在 Locust 压测过程中观察 Locust 进程与 FastAPI 服务进程的资源变化，包括：

- CPU 累计使用时间
- 内存占用变化
- 请求响应时间
- 请求失败情况

通过持续采样观察服务在不同负载下的资源使用趋势。

### 3. 分析目的

将接口层性能指标与 Python 函数级性能分析结合，区分 API 请求处理开销和具体业务函数开销，避免仅凭接口响应时间判断代码瓶颈。


## 9. 关键词匹配算法优化

针对内容审核中的关键词扫描逻辑，开展多种字符串匹配方案的性能对比实验。

### 1. 对比方案

实验比较以下实现：

| 算法 | 实现方式 |
|---|---|
| Naive | 逐个遍历关键词，判断是否存在于文本中 |
| Regex | 使用正则表达式进行关键词匹配 |
| Aho-Corasick | 使用 AC 自动机进行多模式字符串匹配 |
| Python in | 使用 Python 原生字符串包含判断 |

### 2. 大规模关键词实验

在包含约 1,003 个关键词的实验中，以判断风险类别是否命中为目标：

- 正则方案明显快于逐个关键词扫描。
- AC 自动机也快于逐个关键词扫描。
- 本次实验中，正则方案快于 AC 自动机实现。

### 3. 正式业务场景微基准

进一步针对 ContentGuard V1 的实际业务情况进行测试。

当前 V1 仅包含两个关键词：

- 严重违规
- 低风险

对 Python 原生 `in` 判断与预编译正则进行对比：

| 匹配方案 | 中位数耗时 |
|---|---:|
| Python in | 0.1106 μs |
| 预编译 Regex | 0.2353 μs |

实验结果显示，Python 原生 `in` 方案约快 2.13 倍。

### 4. 最终优化决策

正式 V1 保留 Python 原生 `in` 方案，原因：

1. 当前关键词数量较少，没有必要引入更复杂的匹配机制。
2. 实测性能优于预编译正则。
3. 代码结构简单，维护成本更低。
4. 正则和 AC 自动机实验保留在性能研究材料中，作为后续关键词规模扩大时的技术参考。

**优化总结：** 不盲目追求复杂算法，而是结合实际业务规模、性能测试结果和代码维护成本选择合适的实现方案。

## 10. 测试报告

项目支持使用 pytest-html 和 Allure 生成测试报告。

### 10.1 pytest-html 报告

执行：

```powershell
python -m pytest --html=report.html --self-contained-html
```

生成：

```text
report.html
```

### 10.2 Allure 报告

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

## 11. 代码覆盖率分析

项目使用 Coverage.py 进行语句覆盖率和分支覆盖率分析。

### 11.1 安装 Coverage.py

```powershell
python -m pip install coverage
```

### 11.2 执行覆盖率统计

```powershell
python -m coverage erase

python -m coverage run --branch -m pytest

python -m coverage report -m
```

### 11.3 生成 HTML 覆盖率报告

```powershell
python -m coverage html
```

打开报告：

```powershell
start htmlcov/index.html
```

### 11.4 覆盖率结果

项目在当前测试范围内达到：

| 指标 | 最终结果 |
|---|---:|
| 语句覆盖率 | 100% |
| 分支覆盖率 | 100% |
| 未执行语句 | 0 |
| 未完全覆盖分支 | 0 |

通过覆盖率报告定位未执行代码和未覆盖分支，并针对输入校验、异常处理及接口业务路径补充测试用例。

**说明：100% 代码覆盖率不代表系统不存在 Bug，也不代表所有可能输入和业务场景均已验证。**

## 12. 缺陷注入实验

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

## 13. CI 自动化测试

项目配置 GitHub Actions 工作流：

```text
.github/workflows/tests.yml
```

用于在 GitHub Actions 环境中执行自动化测试。

工作流的实际执行状态可以在 GitHub 仓库的 Actions 页面查看：

https://github.com/6Maodie6/ContentGuard/actions

## 14. 项目实践收获

通过 ContentGuard 项目，完成了从接口开发、自动化测试到性能分析和工程化管理的完整实践，主要收获如下：

1. **接口服务开发：** 使用 FastAPI 搭建模拟内容审核服务，实现内容审核、任务创建、任务查询和人工审核等核心接口。
2. **自动化测试体系：** 使用 pytest 构建接口自动化测试体系，按照业务功能组织测试代码。
3. **测试用例设计：** 运用等价类划分、边界值分析和参数化测试，提高测试场景覆盖的完整性。
4. **测试资源管理：** 使用 pytest fixture 管理测试客户端及公共测试资源，降低测试代码重复。
5. **业务流程测试：** 针对人工审核任务设计状态迁移测试，验证任务从创建、查询到审核完成的完整业务流程。
6. **版本 Diff 测试：** 对比 V1、V2 两个版本的审核结果，识别新增规则带来的预期行为差异，验证版本变更的正确性。
7. **覆盖率分析：** 使用 Coverage.py 分析语句覆盖率和分支覆盖率，辅助发现未覆盖的代码路径。
8. **缺陷检测能力验证：** 通过缺陷注入实验，验证测试用例对代码缺陷的发现能力。
9. **自动化测试报告：** 使用 Allure 和 pytest-html 生成测试报告，提升测试结果的可读性和可追溯性。
10. **性能测试实践：** 使用 Locust 设计不同并发用户数和启动速率的压测场景，测试审核接口及完整业务链路，并观察响应时间、吞吐量和请求失败情况。
11. **性能分析与优化：** 使用 cProfile 分析代码执行耗时，对比原生字符串匹配、正则表达式和 Aho-Corasick 自动机等关键词匹配方案，并根据实际测试结果选择更适合当前业务规模的实现。
12. **工程化与持续集成：** 使用 Git、GitHub 管理项目代码，并通过 GitHub Actions 配置自动化测试流程，实践持续集成的基本过程。

通过以上实践，初步建立了从需求分析、测试用例设计、自动化执行、缺陷分析到性能测试和持续集成的测试开发工作流程。

## 15. 后续改进方向

当前 ContentGuard 是一个用于测试开发学习和实践的模拟内容审核系统。虽然已经完成接口自动化测试、性能测试、版本 Diff 测试及基础工程化建设，但在系统架构和测试深度方面仍有进一步完善空间：

- **数据库持久化：** 将当前基于内存字典的任务存储方式改为 SQLite、MySQL 或 PostgreSQL，实现任务数据持久化，并测试数据库读写及异常场景。
- **真实审核能力：** 引入更丰富的内容审核规则，或接入真实 AI 模型，扩展审核场景，验证模型输出及接口行为。
- **性能测试深化：** 扩展 Locust 测试场景，进一步分析不同并发规模下的系统吞吐量、响应时间、资源占用及性能瓶颈，也可以引入 JMeter 进行对比实践。
- **并发与稳定性测试：** 验证多个审核请求同时执行时的任务状态一致性，重点关注重复审核、并发状态更新及异常恢复等场景。
- **测试体系完善：** 补充权限控制、安全性、接口兼容性、异常处理和边界场景测试，进一步提高测试体系的完整性。
- **持续集成完善：** 优化 GitHub Actions 工作流，逐步加入覆盖率门禁、测试报告归档及自动化质量检查。


## 16. License

本项目主要用于个人学习、测试开发实践及技术交流。

