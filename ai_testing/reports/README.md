# AI Testing Reports

本目录用于保存 ContentGuard 项目中的 AI 测试实验结果，采用 JSON 格式记录模型评估、安全测试、Prompt 版本对比和稳定性测试数据。

## 1. 目录结构

```text
reports/
├── README.md
├── evaluation_reports/
│   ├── evaluation_ollama_v1.json
│   ├── evaluation_ollama_v1_dataset_v1.json
│   ├── evaluation_ollama_v2.json
│   ├── evaluation_ollama_v2_dataset_v1.json
│   └── evaluation_report_v1.json
│
├── prompt_comparison_reports/
│   └── prompt_comparison_v1_vs_v2.json
│
├── security_reports/
│   ├── security_comparison.json
│   ├── security_ollama_v2_full10_temp_0.json
│   ├── security_ollama_v2_temp_0.0.json
│   ├── security_ollama_v3_full10_temp_0.json
│   ├── security_ollama_v3_temp_0.0.json
│   └── security_ollama_v4_temp_0.0.json
│
└── stability_reports/
    ├── stability_comparison_v2.json
    ├── stability_ollama_v2.json
    ├── stability_ollama_v2_temp_0.3.json
    └── stability_ollama_v2_temp_0.7.json
```

## 2. 报告分类

### 2.1 evaluation_reports

保存模型在 Golden Dataset 上的评估结果。

主要记录：
- Prompt 版本
- 模型及参数配置
- 测试样本数量
- 预测结果
- Accuracy、Precision、Recall、F1-score 等分类指标

### 2.2 prompt_comparison_reports

保存不同 Prompt 版本的普通评估结果对比。

当前包含 V1 与 V2 的对比报告，用于分析版本迭代前后的分类指标变化，以及测试样本的修复和回归情况。

### 2.3 security_reports

保存 AI 内容审核安全测试结果。

主要记录：
- 正常基线样本和攻击样本的预测结果
- 攻击样本准确率
- 攻击抵抗率
- 成对一致率
- 不同 Prompt 版本的修复和回归情况

当前保留 Prompt V2、V3、V4 的安全测试报告及版本对比报告。

### 2.4 stability_reports

保存不同 Temperature 参数下的模型重复请求测试结果。

主要记录：
- 每条样本的重复预测结果
- 各审核标签的出现次数
- 单条样本的一致率
- 完全稳定样本数量
- 整体稳定率和平均一致率

当前包含 Prompt V2 在不同 Temperature 配置下的实验报告，以及稳定性对比报告。

## 3. 报告使用说明

JSON 报告用于保存实验数据和分析结果，可以作为后续版本对比、实验复现和项目总结的依据。

注意：
- 不同报告进行对比时，应确保测试数据集、模型和实验参数满足可比条件。
- 不同 Temperature 的稳定性报告用于分析参数变化对输出一致性的影响。
- 安全测试结果只反映当前测试集和模型配置下的表现，不代表模型能够抵御所有攻击。
- 实验报告应保留实际运行结果，不应手动修改指标来美化实验数据。