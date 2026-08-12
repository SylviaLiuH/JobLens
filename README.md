# JobLens

## 项目简介

JobLens 是一个面向大学生和应届毕业生的 AI 求职岗位分析工具。

项目通过收集和分析真实招聘 JD，帮助用户了解目标岗位的技能要求、
招聘趋势以及自身能力缺口。

## 核心功能

1. 招聘岗位数据整理与存储
2. 岗位技能关键词统计
3. 招聘数据可视化
4. AI JD 分析
5. 简历与岗位匹配分析

## 技术栈

Python
SQL
Pandas
Data Visualization
LLM API
Streamlit

## 当前进度

Project Day 1 - 项目需求设计

### 2026-08-11

已完成 JobLens 第一版数据分析流程：

- 收集 5 条真实外企招聘岗位数据
- 使用 Pandas 读取 CSV 数据
- 检查并处理缺失值
- 建立 raw / processed 数据目录
- 对岗位类别进行标准化
- 拆分并统计岗位技能关键词
- 对 AI / GenAI 等技能名称进行标准化
- 生成岗位类别分布图
- 生成 Top 10 技能频次图

### 当前数据规模

- 岗位数量：5
- 数据字段：13
- 数据来源：企业官方招聘网站

> 当前样本量较小，分析结果仅用于验证数据处理流程，不代表整体招聘市场趋势。

## 2026-08-12 — Greenhouse 多公司岗位采集器 V0.2

今天完成了 JobLens 招聘数据采集模块的扩展，将原本针对少量公司的测试脚本升级为可配置、可批量运行的 Greenhouse 数据采集器。

### 已完成

* 使用 Greenhouse Job Board API 获取真实招聘岗位数据
* 将公司信息从 Python 代码中分离，新增 `config/greenhouse_companies.csv`
* 支持通过配置文件批量管理 Greenhouse 公司及 `board_token`
* 批量采集 11 家公司的招聘岗位
* 自动筛选中国地区相关岗位
* 自动识别实习 / 应届岗位关键词：

  * Intern
  * Internship
  * Graduate
  * New Grad
  * Entry Level
* 增加异常处理，单个公司采集失败不会导致整个程序中止
* 将不同公司的 API 数据统一转换为 JobLens 数据格式
* 自动记录：

  * 公司名称
  * 岗位名称
  * 工作地点
  * JD 原始 HTML
  * 岗位链接
  * 发布时间
  * 更新时间
  * 是否为目标岗位
  * 数据来源
  * 数据采集日期

### 本次采集结果

* 配置公司数量：11
* 成功采集公司：11
* 失败公司：0
* 中国相关岗位：78
* 实习 / 应届目标岗位：4

生成的数据文件：

```text
data/raw/
├─ greenhouse_china_jobs.csv
├─ greenhouse_target_jobs.csv
└─ greenhouse_collection_summary.csv
```

### 数据质量检查

对自动筛选出的目标岗位进行了人工检查。

当前 `is_target` 规则能够较准确地识别岗位是否属于实习 / 应届类型，但进一步发现：

**“属于实习岗位”并不等于“适合某位求职者申请”。**

真实 JD 中还可能存在：

* 本科 / 硕士 / 博士学历限制
* 毕业年份限制
* 专业限制
* 实习时长和每周出勤要求
* 英语要求
* 工作地点限制
* 技能和工作经验要求

因此后续 JobLens 将把岗位分析拆分成两个层次：

```text
岗位类型识别
    ↓
个人申请资格判断
    ↓
技能匹配与 Skill Gap
    ↓
最终岗位匹配结果
```

### 下一步

下一阶段将开始处理 JD 文本：

* 清洗 Greenhouse 返回的 HTML
* 提取结构化岗位要求
* 提取 Education / Graduation / Skills / English 等字段
* 为后续 AI JD Analysis 和 Resume-Job Matching 做准备

> 当前数据集仍处于项目早期阶段，采集结果主要用于验证数据采集、清洗和分析流程，不代表整体招聘市场情况。
