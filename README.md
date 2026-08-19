# 🔎 JobLens

**AI-powered Job Market Analysis & Candidate Matching Assistant**

JobLens 是一个面向学生与应届生的招聘岗位分析项目：从真实招聘 API 获取岗位数据，将非结构化 JD 清洗并结构化，再进行市场分析、候选人 Skill Gap 与岗位匹配。

## ✨ V1.0 功能

- Greenhouse 多公司岗位采集（配置驱动）
- 中国地区岗位筛选与采集统计
- HTML JD → 干净文本
- 公司 / 岗位 / 地点标准化与双层去重
- Skills / Education / English / Experience / Graduation Year 自动提取
- SQLite 数据库
- 公司 / 地点 / 类别 / Skill 统计与可视化
- Candidate Profile + Match Score + Skill Gap
- Streamlit Dashboard / Job Browser / JD Analyzer / Job Match
- 可选 LLM 深度 JD 分析

## 🧱 项目结构

```text
JobLens/
├─ config/
│  ├─ greenhouse_companies.csv
│  └─ candidate_profile.json
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ joblens.db
├─ outputs/
│  ├─ figures/
│  ├─ tables/
│  └─ insights.md
├─ joblens_core.py
├─ collect_greenhouse.py
├─ clean_jobs.py
├─ standardize_jobs.py
├─ extract_requirements.py
├─ build_database.py
├─ matcher.py
├─ ai_analyzer.py
├─ analyze_jobs.py
├─ pipeline.py
├─ app.py
├─ requirements.txt
└─ resume_project_bullets.md
```

## 🚀 Windows 快速启动

### 1. 安装依赖

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 使用项目自带数据跑完整 pipeline

```powershell
python pipeline.py
```

### 3. 启动 Web Demo

```powershell
streamlit run app.py
```

也可以直接双击：

```text
run_pipeline.bat
run_app.bat
```

## 🔄 重新抓取最新岗位（可选）

```powershell
python collect_greenhouse.py
python pipeline.py
```

公司列表放在：

```text
config/greenhouse_companies.csv
```

以后新增 Greenhouse 公司时，只需要增加 `company,board_token`，不用改采集逻辑。

## 🤖 可选 AI 深度分析

本地规则提取与匹配 **不需要 API Key**。

如果希望在 Streamlit 中启用 AI 深度分析：

```powershell
$env:OPENAI_API_KEY="你的 API Key"
$env:OPENAI_MODEL="gpt-5.6"
streamlit run app.py
```

`OPENAI_MODEL` 可以按你的账号可用模型调整。

## 📊 当前随项目打包的数据快照

- 数据采集日期：2026-08-12
- Greenhouse 配置公司：11
- 中国岗位原始记录：78
- 标准化去重后：运行 `pipeline.py` 后以终端输出为准

数据快照用于展示 pipeline，不代表整体招聘市场。

## 🧠 Matching 说明

Match Score 是启发式项目功能，主要用于展示：

- JD skills ↔ candidate skills
- Education eligibility
- English requirement
- Experience risk
- Graduation-year constraint
- Skill Gap

**它不是录用概率预测。**

## 📌 Portfolio Value

这个项目重点展示：

`Python + Pandas + REST API + Data Cleaning + Regex/NLP-style Extraction + SQLite + Data Analysis + LLM Integration + Streamlit + Git`

简历项目描述见：[`resume_project_bullets.md`](resume_project_bullets.md)

## License / Data Note

Job data belongs to the original employers and is used here only as a small portfolio/data-processing snapshot. Source URLs are preserved for traceability. The collector uses the public Greenhouse Job Board GET API.
