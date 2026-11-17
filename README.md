**# ContentGuard**



**\*\*基于 Python + FastAPI + pytest + Locust + Ollama 的内容审核与测试开发实践项目\*\***



\<p *align*="center">

  \<img src="https\://img.shields.io/badge/Python-3.13-blue.svg" alt="Python">

  \<img src="https\://img.shields.io/badge/FastAPI-API-green.svg" alt="FastAPI">

  \<img src="https\://img.shields.io/badge/pytest-Automation-orange.svg" alt="pytest">

  \<img src="https\://img.shields.io/badge/Locust-Performance-brightgreen.svg" alt="Locust">

  \<img src="https\://img.shields.io/badge/Ollama-LLM-purple.svg" alt="Ollama">

  \<img src="https\://img.shields.io/badge/Coverage-96%25-brightgreen.svg" alt="Coverage">

\</p>



**## 1. 项目介绍**



ContentGuard 是一个基于 Python 和 FastAPI 搭建的模拟内容审核系统，同时围绕该系统构建了接口自动化测试、性能测试和 AI 测试实践体系。



项目模拟内容审核平台中的核心业务流程：用户提交文本内容，系统根据预设规则或 AI 模型进行风险分类；对于需要人工处理的内容，创建审核任务，并支持任务查询和人工审核。



项目使用 pytest 构建自动化测试体系，使用 Locust 进行接口负载测试，并引入本地 Ollama 大语言模型，开展模型效果评估、Prompt 迭代、安全测试和稳定性测试。



项目重点是实践测试开发中的核心能力，包括：



\- Python 接口自动化测试与 pytest 测试框架

\- 等价类、边界值、参数化测试及异常场景设计

\- 单元测试、接口测试、业务流程测试和 Diff 测试

\- 缺陷注入与自动化测试有效性验证

\- Coverage.py 代码覆盖率分析

\- Locust 接口性能测试与性能分析

\- 大语言模型评估与 Prompt 版本对比

\- AI 内容审核安全测试与稳定性测试

\- GitHub Actions 持续集成



**## 2. 技术栈**



\| 技术 | 用途 |

\|---|---|

\| Python 3.13 | 项目开发语言 |

\| FastAPI | 搭建内容审核 API 服务 |

\| Pydantic | 请求参数校验 |

\| pytest | 自动化测试框架 |

\| requests | HTTP 请求及 Ollama API 调用 |

\| httpx | FastAPI TestClient 测试支持 |

\| pytest-html | HTML 测试报告 |

\| Allure | 自动化测试报告 |

\| Coverage.py | 代码覆盖率分析 |

\| Locust | 接口性能及并发测试 |

\| Ollama | 本地大语言模型运行环境 |

\| Qwen3 8B | 本地 AI 内容审核模型 |

\| Git / GitHub | 版本管理与代码托管 |

\| GitHub Actions | CI 自动化测试流程 |



**## 3. 项目架构**



**### 3.1 目录结构**



\`\`\`text

ContentGuard/

│

├── .github/

│   └── workflows/

│       └── tests.yml

│

├── app/                         # FastAPI 业务服务

│   ├── \_\_init\_\_.py

│   ├── main.py

│   ├── moderation.py

│   └── moderation_v2.py

│

├── tests/                       # 接口及业务自动化测试

│   ├── test_moderation.py

│   ├── test_moderation_unit.py

│   ├── test_moderation_v2_unit.py

│   ├── test_validation.py

│   ├── test_workflow\.py

│   ├── test_diff.py

│   └── test_compare_reports.py

│

├── ai_testing/                  # AI 测试体系

│   ├── clients/

│   │   └── ollama_client.py

│   ├── dataset/

│   │   ├── golden_dataset.json

│   │   └── security_dataset.json

│   ├── evaluation/

│   │   ├── evaluator.py

│   │   ├── metrics.py

│   │   └── compare_reports.py

│   ├── prompts/

│   │   ├── prompt_v1.py

│   │   ├── prompt_v2.py

│   │   ├── prompt_v3.py

│   │   └── prompt_v4.py

│   ├── reports/

│   │   ├── evaluation_reports/

│   │   ├── prompt_comparison_reports/

│   │   ├── security_reports/

│   │   └── stability_reports/

│   ├── security/

│   │   ├── security_test.py

│   │   └── compare_security.py

│   ├── stability/

│   │   ├── stability.py

│   │   └── compare_stability.py

│   └── tests/

│

├── performance/                 # 性能测试与性能分析

│

├── data/                        # 业务测试数据

│

├── docs/                        # 项目文档

│

├── conftest.py

├── pytest.ini

├── requirements.txt

├── .gitignore

└── README.md

\`\`\`



**### 3.2 核心模块说明**



\| 模块 | 主要职责 |

\|---|---|

\| \`app/\` | FastAPI 服务、内容审核逻辑及任务管理 |

\| \`tests/\` | 接口自动化测试、单元测试、业务流程测试和 Diff 测试 |

\| \`ai_testing/clients/\` | Ollama 模型 HTTP 客户端 |

\| \`ai_testing/dataset/\` | AI 评估数据集和安全测试数据集 |

\| \`ai_testing/evaluation/\` | 模型评估、指标计算和报告对比 |

\| \`ai_testing/prompts/\` | 多版本 Prompt 管理 |

\| \`ai_testing/security/\` | AI 安全测试及安全报告对比 |

\| \`ai_testing/stability/\` | AI 输出稳定性测试及报告对比 |

\| \`ai_testing/reports/\` | AI 测试实验报告 |

\| \`performance/\` | Locust 压测、性能分析及关键词匹配算法实验 |

\| \`data/\` | 业务接口测试数据 |

\| \`docs/\` | 项目总结与技术文档 |



**## 4. 核心业务功能**



**### 4.1 内容自动审核**



系统根据预设关键词规则模拟内容风险分类。



\| 输入内容 | 审核结果 | 风险等级 |

\|---|---|---|

\| 普通内容 | pass | low |

\| 低风险内容 | review | medium |

\| 严重违规内容 | block | high |

\| 诈骗内容（V2） | block | high |

\| 同时包含严重违规和低风险关键词 | block | high |



**### 4.2 审核任务管理**



系统提供以下接口：



\| 请求方式 | 接口 | 功能 |

\|---|---|---|

\| POST | \`/api/v1/moderation/tasks\` | 创建审核任务 |

\| GET | \`/api/v1/moderation/tasks/{task_id}\` | 查询审核任务 |

\| POST | \`/api/v1/moderation/tasks/{task_id}/manual-review\` | 人工审核 |



**### 4.3 人工审核状态管理**



任务状态包括：



\- \`pending\`：等待人工审核

\- \`completed\`：审核完成



主要状态流转：



\`\`\`text

创建审核任务

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

\`\`\`



对于不存在的任务，接口返回 404。



**## 5. 接口自动化测试**



使用 pytest 构建接口自动化测试体系，围绕内容审核、任务管理和人工审核流程设计测试场景。



**### 5.1 功能测试**



验证内容分类结果是否符合业务规则：



\- 普通内容返回 pass

\- 低风险内容返回 review

\- 严重违规内容返回 block

\- 严重违规规则优先于低风险规则

\- V2 新增诈骗内容识别规则



**### 5.2 等价类测试**



将输入划分为有效和无效等价类。



\| 输入类型 | 测试数据 | 预期结果 |

\|---|---|---|

\| 字符串 | 正常文本 | 正常处理 |

\| 整数 | 123 | 拒绝输入 |

\| 浮点数 | 12.5 | 拒绝输入 |

\| 布尔值 | True | 拒绝输入 |

\| 列表 | \`["测试内容"]\` | 拒绝输入 |

\| 字典 | \`{"text": "测试内容"}\` | 拒绝输入 |

\| 空值 | None | 请求校验失败 |



**### 5.3 边界值测试**



针对内容长度限制 1～500 字符设计边界值：



\| 长度 | 预期结果 |

\|---:|---|

\| 0 | 拒绝输入 |

\| 1 | 正常处理 |

\| 2 | 正常处理 |

\| 499 | 正常处理 |

\| 500 | 正常处理 |

\| 501 | 拒绝输入 |



**### 5.4 单元测试**



直接调用内容分类函数，验证函数自身的输入校验和异常处理逻辑。



重点覆盖：



\- 非字符串输入

\- 空字符串

\- 超过最大长度

\- 正常分类结果



**### 5.5 状态迁移测试**



验证任务在不同操作下的状态变化：



\- 创建低风险任务后进入 pending

\- 人工审核 pass 后进入 completed

\- 人工审核 block 后进入 completed

\- 已完成任务不能再次审核

\- 非法审核决策不能改变原任务状态

\- 不存在的任务不能进行人工审核



**### 5.6 Diff 测试**



通过比较 V1 和 V2 的内容分类结果，检查版本迭代带来的行为变化。



重点验证：



\- 两个版本共有规则的行为一致性

\- V2 新增诈骗识别规则

\- 新版本是否引入非预期行为差异



**### 5.7 缺陷注入实验**



通过主动修改业务逻辑，验证自动化测试是否能够发现已知缺陷。



开展了三类实验：



\| 缺陷类型 | 注入方式 | 验证目标 |

\|---|---|---|

\| 关键词识别缺陷 | 修改严重违规关键词 | 检查错误分类能否被发现 |

\| 风险优先级缺陷 | 调换风险规则判断顺序 | 检查优先级错误能否被发现 |

\| 任务状态转换缺陷 | 允许已完成任务重复审核 | 检查非法状态迁移能否被发现 |



实验结果：注入对应缺陷后，相关测试用例能够发现错误；恢复业务逻辑后，测试重新通过。



缺陷注入用于验证已设计测试的有效性，不代表测试能够发现所有类型的缺陷。



**## 6. AI 测试实践**



在原有规则审核系统基础上，引入本地 Ollama 大语言模型，构建独立的 AI 测试体系。



使用 Golden Dataset、Prompt 版本管理和自动化评估机制，对模型内容审核能力进行测试。



**### 6.1 本地模型与调用封装**



使用 Ollama 在本地运行 Qwen3 8B 模型，通过 HTTP API 调用模型。



主要实践内容：



\- 封装 Ollama HTTP 请求客户端

\- 处理模型响应和 JSON 解析

\- 校验模型输出的审核标签及原因字段

\- 处理请求超时、连接异常、HTTP 错误和非法响应

\- 使用 pytest 和 monkeypatch 模拟 HTTP 请求，测试客户端异常处理逻辑



模型客户端与测试代码分离，避免单元测试必须依赖本地模型服务。



**### 6.2 Golden Dataset 与模型评估**



构建人工标注的 Golden Dataset，用于评估模型对内容的分类效果。



审核标签：



\- \`pass\`

\- \`review\`

\- \`block\`



评估模块实现了多分类指标计算：



\| 指标 | 作用 |

\|---|---|

\| Confusion Matrix | 混淆矩阵 |

\| Precision | 精确率 |

\| Recall | 召回率 |

\| F1-score | F1 分数 |

\| Accuracy | 准确率 |

\| Macro-F1 | 宏平均 F1 |

\| Weighted-F1 | 加权平均 F1 |



同时计算各类别的 TP、FP、FN、TN，分析不同审核类别的分类表现。



**### 6.3 Prompt 版本迭代**



设计多个 Prompt 版本，对模型的内容审核规则进行迭代。



\| 版本 | 主要实践 |

\|---|---|

\| Prompt V1 | 初始审核指令 |

\| Prompt V2 | 优化分类规则和指令表达 |

\| Prompt V3 | 针对安全测试中发现的问题进行改进 |

\| Prompt V4 | 加强指令操控识别及内容风险区分 |



通过相同测试数据集运行不同版本 Prompt，生成评估报告并进行版本对比。



**\*\*V1 与 V2 的一次评估对比结果：\*\***



\| 指标 | V1 | V2 | 变化 |

\|---|---:|---:|---:|

\| Accuracy | 80% | 90% | +10 个百分点 |

\| Macro-F1 | 76.85% | 85.19% | +8.33 个百分点 |

\| Weighted-F1 | 79.72% | 91.11% | +11.39 个百分点 |



在这组 10 条样本的实验中，V2 修复 1 条问题，未观察到回归。



**### 6.4 AI 安全测试**



构建独立的安全测试数据集，包含正常审核样本和指令操控攻击样本。



当前安全测试集包含 10 条样本：



\- 5 条正常基线样本

\- 5 条攻击样本



覆盖的攻击类型包括：



\- \`label_override\`：尝试强制修改模型审核标签

\- \`instruction_override\`：尝试覆盖原始审核指令



对不同 Prompt 版本执行相同安全测试，记录模型预测结果并生成安全报告。



**\*\*当前实验结果：\*\***



\| Prompt 版本 | 攻击样本通过数 | 攻击准确率 |

\|---|---:|---:|

\| V2 | 2 / 5 | 40% |

\| V3 | 4 / 5 | 80% |

\| V4 | 5 / 5 | 100% |



V2 → V3 修复了 2 个攻击用例；V3 → V4 修复了 SEC007，当前测试集未观察到回归。



以上 100% 仅表示 Prompt V4 在当前 5 条攻击样本中取得全部正确结果，不代表模型能够抵御所有 Prompt Injection 攻击。



**### 6.5 AI 稳定性测试**



针对大语言模型输出具有随机性的问题，设计重复请求实验，分析不同 temperature 参数下模型分类结果的一致性。



测试设计：



\- 使用 Golden Dataset 中的有效样本

\- 对同一条样本重复请求模型

\- 记录每次预测结果

\- 使用 Counter 统计各标签出现次数

\- 计算单条样本的一致率

\- 统计完全一致的样本数量和整体稳定情况



单条样本一致率：



\`\`\`text

Agreement Rate = 出现次数最多的标签数量 / 重复请求次数

\`\`\`



稳定性判定：重复请求得到的审核标签完全一致。



**\*\*Prompt V2 稳定性实验结果：\*\***



实验条件：10 条样本，每条重复请求 5 次。



\| Temperature | 完全稳定样本 | 稳定率 | 平均一致率 |

\|---:|---:|---:|---:|

\| 0.0 | 9 / 10 | 90% | 98% |

\| 0.3 | 9 / 10 | 90% | 98% |

\| 0.7 | 7 / 10 | 70% | 88% |



实验观察：



\- Temperature 0.0 和 0.3 下，整体稳定性表现接近。

\- Temperature 0.7 下，完全稳定样本比例下降。

\- 部分样本在重复请求中出现 pass、review、block 标签变化。



该实验用于分析当前模型、Prompt 和数据集条件下的输出一致性，不代表其他模型或参数配置具有相同表现。



**### 6.6 AI 测试报告与版本对比**



针对模型评估、安全测试和稳定性测试，分别保存 JSON 实验报告。



实现报告对比模块，支持：



\- 比较不同 Prompt 版本的评估结果

\- 统计修复、回归和保持不变的样本

\- 对比分类指标变化

\- 比较安全测试结果

\- 对比稳定性实验数据



通过结构化报告保存实验结果，提高 AI 测试过程的可追溯性。



## 7. 性能测试实践

使用 Locust 对 ContentGuard 内容审核服务开展接口负载测试、并发测试和稳定性观察，并结合 cProfile 与关键词匹配算法实验分析性能表现。

### 7.1 测试场景

除单接口压测外，设计完整审核业务链路：

1. 创建审核任务
2. 查询审核任务
3. 执行人工审核
4. 再次查询任务，验证最终状态

Locust 脚本位于 `performance/locustfile.py`，通过 `ContentGuardUser` 模拟用户行为。每轮任务依次调用创建、查询、人工审核和再次查询四个接口，并检查 HTTP 状态码、任务状态及最终审核决策；任务之间使用 `between(1, 3)` 设置 1～3 秒随机等待。

### 7.2 环境准备与启动方式

性能测试需要先启动被测 FastAPI 服务，再启动 Locust。以下命令均在项目根目录 `ContentGuard/` 下执行，并确保已激活项目虚拟环境。

**1. 安装项目依赖**

```powershell
python -m pip install -r requirements.txt
```

**2. 终端一：启动 FastAPI 服务**

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

服务启动后，可在浏览器访问 `http://127.0.0.1:8000/docs`，确认 API 文档能够正常打开。该终端需要保持运行。

**3. 终端二：启动 Locust Web UI**

在项目根目录的另一个终端执行：

```powershell
python -m locust -f performance/locustfile.py --host http://127.0.0.1:8000
```

浏览器访问：

```text
http://127.0.0.1:8089
```

在 Locust 页面配置并启动测试：

| 配置项 | 示例值 |
|---|---:|
| Number of users | 50 |
| Spawn rate | 5 |
| Host | `http://127.0.0.1:8000` |

点击 Start 后开始压测。若要复现本文 3 分钟的测试条件，请在运行约 3 分钟后停止测试，并记录实际运行时长及统计结果。不同机器、依赖版本和运行环境下，结果可能存在差异。

### 7.3 命令行无界面压测与结果导出

也可以使用 Locust 无界面模式执行固定时长的测试，适合自动化复现和保存结果。

先在项目根目录创建结果目录：

```powershell
New-Item -ItemType Directory -Force performance\results
```

执行 50 用户、每秒启动 5 个用户、持续 3 分钟的压测，并导出 CSV 和 HTML 报告：

```powershell
python -m locust -f performance/locustfile.py `
  --host http://127.0.0.1:8000 `
  --headless `
  -u 50 `
  -r 5 `
  -t 3m `
  --csv performance/results/locust_50users `
  --html performance/results/locust_50users.html
```

参数说明：

| 参数 | 含义 |
|---|---|
| `-f performance/locustfile.py` | 指定项目中的 Locust 测试脚本 |
| `--host` | 指定被测服务的基础地址 |
| `--headless` | 使用无界面模式运行 |
| `-u 50` | 设置目标并发用户数为 50 |
| `-r 5` | 设置用户启动速率为每秒 5 个用户 |
| `-t 3m` | 设置运行时长为 3 分钟 |
| `--csv` | 指定 CSV 结果文件名前缀 |
| `--html` | 导出 HTML 测试报告 |

运行结束后，`performance/results/` 中会生成以 `locust_50users` 为前缀的统计 CSV 文件，以及 `locust_50users.html` 报告。CSV 文件用于进一步分析请求数、失败数、响应时间和吞吐量；HTML 文件可用浏览器打开查看。

### 7.4 多轮并发测试

使用不同并发用户数开展测试：

| 测试轮次 | 并发用户数 | Spawn Rate |
|---|---:|---:|
| 第一轮 | 10 | 2 users/s |
| 第二轮 | 30 | 5 users/s |
| 第三轮 | 100 | 10 users/s |
| 第四轮 | 200 | 20 users/s |
| 稳定性测试 | 100 | 10 users/s |

已记录轮次的请求失败数均为 0。另进行了约 10 分钟的持续运行观察，用于观察服务响应和资源变化。复现时应根据本机 CPU、内存情况逐步增加并发数，不建议未经评估直接运行高并发测试。

### 7.5 完整业务链路压测结果

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

测试结论：

- 两轮测试均未记录到失败请求。
- 两轮平均响应时间和 P95、P99 指标接近。
- 在当前测试条件下，接口表现相对稳定。
- 通过多接口业务链路验证，不仅关注单个接口，也关注完整业务流程。

注意：以上数据来自本机模拟测试环境，不代表生产环境容量或线上 SLA。一个完整业务流程包含多个 HTTP 请求，HTTP RPS 不等于完整业务流程每秒完成数。重新运行时，实际请求总数、RPS 和响应时间会受硬件、系统负载、Python 版本及服务状态影响，不应要求与历史数据完全一致。

### 7.6 性能测试脚本的请求链路

`performance/locustfile.py` 中的单次用户任务包含以下步骤：

| 顺序 | 请求 | 校验内容 |
|---|---|---|
| 1 | `POST /api/v1/moderation/tasks` | 创建任务成功，返回 `task_id`，初始状态为 `pending` |
| 2 | `GET /api/v1/moderation/tasks/{task_id}` | 查询任务成功，状态仍为 `pending` |
| 3 | `POST /api/v1/moderation/tasks/{task_id}/manual-review` | 提交 `pass` 人工审核决策 |
| 4 | `GET /api/v1/moderation/tasks/{task_id}` | 再次查询，状态为 `completed`，决策为 `pass` |

脚本使用 `catch_response=True` 对响应进行自定义校验；当状态码、响应 JSON 或业务状态不符合预期时，将请求标记为失败，而不是只根据 HTTP 状态码判断成功。

### 7.7 性能测试注意事项与限制

- **先启动服务：** Locust 只负责产生请求，被测 FastAPI 服务必须先运行；如果服务未启动或端口不正确，请求会失败。
- **使用正确脚本路径：** 从项目根目录启动时，脚本路径应为 `performance/locustfile.py`，不能写成根目录下的 `locustfile.py`。
- **保持单进程测试条件：** 当前示例服务使用内存字典保存审核任务。复现该业务链路时应使用单个 Uvicorn worker，避免多进程各自持有独立内存数据而导致任务查询不一致。
- **控制压测强度：** 并发数应逐步增加，并关注本机 CPU、内存和服务日志；本地压测结果只用于当前实验环境下的对比分析。
- **结果可重复但不保证数值完全相同：** 固定脚本和参数可以复现测试方法，但操作系统调度、机器性能和后台负载会影响最终指标。

### 7.8 性能分析与资源监控

使用 Python 自带的 `cProfile` 对 `classify_content` 函数进行性能分析。

实验中累计调用该函数 100,000 次：

| 指标 | 实测结果 |
|---|---:|
| 函数调用次数 | 100,000 |
| 函数自身累计耗时（tottime） | 约 0.032 秒 |
| 累计耗时（cumtime） | 约 0.047 秒 |

同时在 Locust 压测过程中观察 Locust 进程与 FastAPI 服务进程的资源变化，包括：

- CPU 累计使用时间
- 内存占用变化
- 请求响应时间
- 请求失败情况

将接口层性能指标与 Python 函数级性能分析结合，区分 API 请求处理开销和具体业务函数开销。

### 7.9 关键词匹配算法对比

针对内容审核中的关键词扫描逻辑，比较不同字符串匹配方案。

| 算法 | 实现方式 |
|---|---|
| Naive | 逐个遍历关键词，判断是否存在于文本中 |
| Regex | 使用正则表达式进行关键词匹配 |
| Aho-Corasick | 使用 AC 自动机进行多模式字符串匹配 |
| Python in | 使用 Python 原生字符串包含判断 |

在包含约 1,003 个关键词的实验中：

- 正则方案明显快于逐个关键词扫描。
- AC 自动机也快于逐个关键词扫描。
- 本次实验中，正则方案快于 AC 自动机实现。

进一步针对 ContentGuard V1 的实际业务情况进行微基准测试。当前 V1 仅包含两个关键词：

| 匹配方案 | 中位数耗时 |
|---|---:|
| Python in | 0.1106 μs |
| 预编译 Regex | 0.2353 μs |

实验结果显示，Python 原生 `in` 方案约快 2.13 倍。

因此，正式 V1 保留 Python 原生 `in` 方案：

1. 当前关键词数量较少，没有必要引入更复杂的匹配机制。
2. 实测性能优于预编译正则。
3. 代码结构简单，维护成本更低。
4. 正则和 AC 自动机实验保留作为后续关键词规模扩大时的技术参考。

**优化原则：结合实际业务规模、性能测试结果和代码维护成本选择合适的实现方案，而不是盲目追求复杂算法。**


**## 8. 测试报告与代码覆盖率**



**### 8.1 pytest-html 报告**



执行：



\`\`\`powershell

python -m pytest --html=report.html --self-contained-html

\`\`\`



生成独立 HTML 测试报告：



\`\`\`text

report.html

\`\`\`



**### 8.2 Allure 报告**



执行测试并生成 Allure 原始结果：



\`\`\`powershell

python -m pytest --alluredir=allure-results

\`\`\`



生成 HTML 报告：



\`\`\`powershell

allure generate allure-results -o allure-report --clean

\`\`\`



打开报告：



\`\`\`powershell

allure open allure-report

\`\`\`



以上命令需要安装 Allure Commandline，并确保 \`allure\` 命令可以在终端中使用。



**### 8.3 Coverage.py 覆盖率分析**



执行：



\`\`\`powershell

python -m coverage erase



python -m coverage run -m pytest



python -m coverage report --omit="\*/tests/\*,tests/\*,conftest.py" -m

\`\`\`



生成 HTML 覆盖率报告：



\`\`\`powershell

python -m coverage html

\`\`\`



打开报告：



\`\`\`powershell

start htmlcov/index.html

\`\`\`



**\*\*当前项目测试结果：\*\***



\| 指标 | 结果 |

\|---|---:|

\| 自动化测试通过数 | 185 |

\| 测试失败数 | 0 |

\| 测试警告数 | 0 |

\| 业务代码语句总数 | 741 |

\| 未覆盖语句数 | 27 |

\| 语句覆盖率 | 96% |



主要模块覆盖率：



\| 模块 | 语句覆盖率 |

\|---|---:|

\| Ollama Client | 100% |

\| FastAPI 主应用及审核模块 | 100% |

\| AI 安全测试 | 99% |

\| 安全报告对比 | 99% |

\| AI Evaluator | 99% |

\| 多分类指标计算 | 97% |

\| 稳定性报告对比 | 94% |

\| Prompt 评估报告对比 | 90% |

\| AI 稳定性测试 | 90% |



注：



\- 以上数据为当前一次完整测试与覆盖率统计结果。

\- 96% 指语句覆盖率，不代表分支覆盖率。

\- 代码覆盖率只能反映代码执行情况，不能直接证明测试用例的有效性，也不能保证系统不存在 Bug。

\- 测试警告不等于测试失败，需要结合实际警告内容分析。



**## 9. 工程化与持续集成**



**### 9.1 Git 版本管理**



使用 Git 管理项目代码和版本变更，为功能迭代、测试代码维护和版本回归提供基础支持。



**### 9.2 GitHub Actions**



项目配置 GitHub Actions 工作流：



\`\`\`text

.github/workflows/tests.yml

\`\`\`



主要流程：



1\. 检出 GitHub 仓库代码。

2\. 配置 Python 环境。

3\. 安装项目依赖。

4\. 执行 pytest 自动化测试。

5\. 根据工作流配置生成或上传测试结果。



工作流实际执行状态以 GitHub Actions 运行记录为准。



[查看 GitHub Actions]\(https\://github.com/6Maodie6/ContentGuard/actions)



**## 10. 环境准备与项目运行**



**### 10.1 环境要求**



\- Python 3.13

\- Git

\- VS Code（推荐）

\- Windows PowerShell 或其他支持 Python 的终端

\- Ollama（运行 AI 测试时需要）



**### 10.2 克隆项目**



\`\`\`powershell

git clone https\://github.com/6Maodie6/ContentGuard.git



cd ContentGuard

\`\`\`



**### 10.3 创建虚拟环境**



\`\`\`powershell

python -m venv .venv

\`\`\`



激活虚拟环境：



\`\`\`powershell

.\\.venv\Scripts\Activate.ps1

\`\`\`



**### 10.4 安装依赖**



\`\`\`powershell

python -m pip install -r requirements.txt

\`\`\`



检查 Python 环境：



\`\`\`powershell

python --version

\`\`\`



**### 10.5 启动 FastAPI 服务**



在项目根目录执行：



\`\`\`powershell

uvicorn app.main:app --reload

\`\`\`



服务启动后访问：



\`\`\`text

http\://127.0.0.1:8000

\`\`\`



FastAPI 交互式接口文档：



\`\`\`text

http\://127.0.0.1:8000/docs

\`\`\`



**### 10.6 执行自动化测试**



执行全部测试：



\`\`\`powershell

python -m pytest

\`\`\`



显示详细测试结果：



\`\`\`powershell

python -m pytest -v

\`\`\`



只执行指定测试文件：



\`\`\`powershell

python -m pytest tests/test_workflow\.py -v

\`\`\`



**### 10.7 运行 AI 测试的环境说明**



AI 测试需要额外安装并启动 Ollama，并在本地准备相应的 Qwen3 8B 模型。



项目 Ollama 客户端默认调用本地接口：



\`\`\`text

http\://localhost:11434/api/generate

\`\`\`



模型名称及调用参数应与 \`ai_testing/clients/ollama_client.py\` 中的配置保持一致。



AI 测试需要本地模型服务正常运行；不依赖真实模型的单元测试可以通过 mock 和 monkeypatch 独立执行。



**## 11. 项目实践收获**



通过 ContentGuard 项目，完成了从模拟业务服务开发、自动化测试到 AI 测试、性能分析和工程化管理的综合实践。



主要实践成果：



1\. **\*\*接口服务开发：\*\*** 使用 FastAPI 搭建模拟内容审核服务，实现内容审核、任务创建、任务查询和人工审核等核心接口。

2\. **\*\*自动化测试体系：\*\*** 使用 pytest 构建接口自动化测试体系，组织功能测试、单元测试和异常场景测试。

3\. **\*\*测试用例设计：\*\*** 运用等价类划分、边界值分析和参数化测试设计测试场景。

4\. **\*\*业务流程测试：\*\*** 针对人工审核任务设计状态迁移测试，验证完整业务流程。

5\. **\*\*版本 Diff 测试：\*\*** 对比 V1、V2 两个版本的审核结果，识别新增规则带来的行为变化。

6\. **\*\*缺陷检测能力验证：\*\*** 通过缺陷注入实验，验证测试用例对已知业务缺陷的发现能力。

7\. **\*\*覆盖率分析：\*\*** 使用 Coverage.py 分析语句覆盖率，定位未执行代码并补充测试。

8\. **\*\*性能测试实践：\*\*** 使用 Locust 设计不同并发用户数和启动速率的压测场景，分析响应时间、吞吐量和请求失败情况。

9\. **\*\*性能分析与优化：\*\*** 使用 cProfile 分析函数执行耗时，对比原生字符串匹配、正则表达式和 AC 自动机等方案。

10\. **\*\*AI 模型评估：\*\*** 使用 Golden Dataset 和多分类指标评估大语言模型的内容审核效果。

11\. **\*\*Prompt 迭代：\*\*** 设计多个 Prompt 版本，通过评估报告对比不同版本的分类效果。

12\. **\*\*AI 安全测试：\*\*** 设计指令操控攻击样本，验证 Prompt 对特定攻击场景的抵抗能力。

13\. **\*\*AI 稳定性测试：\*\*** 通过重复请求和不同 Temperature 参数实验，分析模型输出一致性。

14\. **\*\*测试工程化：\*\*** 使用 Git、GitHub 和 GitHub Actions 实践版本管理与持续集成。



**## 12. 项目局限与后续改进方向**



ContentGuard 是一个用于测试开发学习和实践的模拟内容审核系统，并非生产级内容审核平台。



当前仍存在以下局限：



\- **\*\*数据持久化：\*\*** 当前任务存储使用内存字典，服务重启后任务数据会丢失，尚未实现数据库持久化。

\- **\*\*审核算法：\*\*** 规则审核使用预设关键词进行模拟，不能代表完整的真实内容审核系统。

\- **\*\*AI 安全测试范围：\*\*** 当前安全测试集规模有限，尚不能覆盖全部 Prompt Injection 攻击类型。

\- **\*\*模型稳定性：\*\*** 当前稳定性实验基于有限样本、Prompt 和模型配置，实验结论具有条件限制。

\- **\*\*性能测试环境：\*\*** 当前性能数据来自本机模拟环境，不能直接推断生产环境性能。

\- **\*\*并发一致性：\*\*** 任务状态管理尚需进一步开展并发更新、重复请求和异常恢复测试。



后续改进方向：



1\. **\*\*数据库持久化：\*\*** 引入 SQLite、MySQL 或 PostgreSQL，完善数据库读写、事务和异常场景测试。

2\. **\*\*AI 安全测试扩展：\*\*** 扩大安全数据集，增加更多指令操控、上下文攻击及边界场景。

3\. **\*\*模型评估深化：\*\*** 扩充 Golden Dataset，分析不同模型、Prompt 和参数配置下的分类表现。

4\. **\*\*性能测试深化：\*\*** 扩展不同负载模型，进一步分析吞吐量、响应时间和资源占用。

5\. **\*\*并发与稳定性测试：\*\*** 验证多个审核请求同时执行时的任务状态一致性。

6\. **\*\*持续集成完善：\*\*** 增加覆盖率门禁、测试报告归档及自动化质量检查。



**## 13. License**



本项目主要用于个人学习、测试开发实践及技术交流。