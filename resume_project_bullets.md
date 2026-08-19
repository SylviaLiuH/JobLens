# JobLens 简历项目描述（可直接改写使用）

## 中文版
**JobLens — AI 求职岗位分析与匹配助手**  | Python / Pandas / SQL(SQLite) / Streamlit / LLM API

- 基于 Greenhouse 公开 Job Board API 构建可配置的多公司招聘数据采集 pipeline，完成中国岗位自动筛选、异常处理、来源追踪与 CSV 持久化；当前项目数据包含 11 个配置公司、78 条采集记录，并清洗去重为 76 条唯一中国岗位。
- 使用 BeautifulSoup、正则表达式与 Pandas 对非结构化 HTML JD 进行清洗和标准化，提取 Skills、Education、English、Experience、Graduation Year 等结构化字段，并导入 SQLite 支持后续查询分析。
- 设计候选人画像与启发式 Job Matching 模块，输出技能匹配、Skill Gap、资格风险提示和匹配评分；使用 Streamlit 构建交互式 Dashboard、JD Analyzer、Job Browser 与 Match 页面。
- 集成可选 LLM 深度分析能力，在配置 API Key 后可对任意 JD 生成岗位概览、关键要求、匹配点、主要缺口和行动建议；无 API Key 时本地规则功能仍可独立运行。

## English version
**JobLens — AI-powered Job Market Analysis & Candidate Matching Assistant** | Python, Pandas, SQLite, Streamlit, LLM API

- Built a configurable multi-company recruitment data pipeline on top of the public Greenhouse Job Board API, including China-location filtering, fault tolerance, source tracking, and CSV persistence; processed 78 collected records into 76 unique China job postings.
- Cleaned and standardized unstructured HTML job descriptions with BeautifulSoup, regex, and Pandas, and extracted structured requirements including skills, education, English, experience, and graduation-year constraints into SQLite.
- Designed a candidate-profile matching module that surfaces skill overlap, skill gaps, eligibility risks, and heuristic match scores, and exposed the workflow through a Streamlit dashboard, JD analyzer, job browser, and matching UI.
- Added optional LLM-powered JD analysis for evidence-based summaries and gap analysis while keeping the core extraction and matching workflow fully functional without an API key.

> 简历上的数字请只在你确认本地运行结果后保留；以后重新抓取数据，数字会变化。
