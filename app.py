from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from ai_analyzer import analyze_jd_with_ai
from joblens_core import (
    categorize_job,
    extract_education,
    extract_english_requirement,
    extract_experience_years,
    extract_graduation_years,
    extract_skills,
    is_target_role,
    join_semicolon,
)
from matcher import load_profile, match_job

DATA_PATH = Path("data/processed/jobs_with_matches.csv")

st.set_page_config(page_title="JobLens", page_icon="🔎", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


st.title("🔎 JobLens")
st.caption("AI-powered job market analysis & candidate-job matching assistant")

if not DATA_PATH.exists():
    st.error("未找到处理后的数据。请先运行：python pipeline.py")
    st.stop()

_df = load_data()
profile = load_profile()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Job Browser", "JD Analyzer", "Job Match", "About"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("岗位数", len(_df))
    c2.metric("公司数", _df["company"].nunique())
    c3.metric("实习/应届", int(_df["is_target"].fillna(False).astype(bool).sum()))
    c4.metric("平均匹配分", round(_df["match_score"].mean(), 1))

    left, right = st.columns(2)
    with left:
        st.subheader("岗位类别")
        st.bar_chart(_df["category"].value_counts())
    with right:
        st.subheader("地点分布")
        st.bar_chart(_df["location"].value_counts().head(12))

    st.subheader("高匹配岗位（本地规则）")
    cols = ["company", "job_title", "location", "category", "match_score", "matched_skills", "missing_skills"]
    st.dataframe(_df[cols].head(15), use_container_width=True, hide_index=True)

with tab2:
    companies = sorted(_df["company"].dropna().unique().tolist())
    categories = sorted(_df["category"].dropna().unique().tolist())
    selected_companies = st.multiselect("公司", companies)
    selected_categories = st.multiselect("类别", categories)
    target_only = st.checkbox("只看实习/应届岗位")

    filtered = _df.copy()
    if selected_companies:
        filtered = filtered[filtered["company"].isin(selected_companies)]
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    if target_only:
        filtered = filtered[filtered["is_target"].fillna(False).astype(bool)]

    st.write(f"共 {len(filtered)} 条")
    show_cols = ["company", "job_title", "location", "category", "education", "english_requirement", "experience_years", "match_score", "source_url"]
    st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

with tab3:
    st.write("粘贴任意 JD，先用本地规则提取结构化要求；配置 API Key 后可再做 AI 深度分析。")
    jd = st.text_area("JD 文本", height=320, placeholder="Paste a job description here...")
    if st.button("本地结构化分析", type="primary", disabled=not jd):
        result = {
            "category": categorize_job("", jd),
            "skills": extract_skills(jd),
            "education": extract_education(jd),
            "english_requirement": extract_english_requirement(jd),
            "experience_years": extract_experience_years(jd),
            "graduation_years": extract_graduation_years(jd),
            "is_target": is_target_role(jd.splitlines()[0] if jd else ""),
        }
        st.json(result)
    if st.button("AI 深度分析", disabled=not jd):
        with st.spinner("AI 分析中..."):
            st.markdown(analyze_jd_with_ai(jd, profile))

with tab4:
    mode = st.radio("输入方式", ["从数据集中选择", "粘贴 JD"], horizontal=True)
    if mode == "从数据集中选择":
        options = _df.apply(lambda r: f"{r['company']} | {r['job_title']} | {r['location']}", axis=1).tolist()
        choice = st.selectbox("选择岗位", options)
        idx = options.index(choice)
        row = _df.iloc[idx]
        local = match_job(row, profile)
        st.metric("Match Score", f"{local['match_score']}/100")
        st.write("**匹配技能：**", local["matched_skills"] or "暂无")
        st.write("**缺口技能：**", local["missing_skills"] or "暂无")
        st.write("**资格/风险提示：**", local["eligibility_notes"] or "暂无明显硬性风险")
        with st.expander("查看 JD"):
            st.write(row.get("description_text", ""))
        if st.button("对这个岗位做 AI 深度分析"):
            with st.spinner("AI 分析中..."):
                st.markdown(analyze_jd_with_ai(str(row.get("description_text", "")), profile))
    else:
        jd2 = st.text_area("粘贴 JD", height=300, key="match_jd")
        if st.button("计算匹配分", disabled=not jd2):
            fake = {
                "skills": join_semicolon(extract_skills(jd2)),
                "education": extract_education(jd2),
                "english_requirement": extract_english_requirement(jd2),
                "experience_years": extract_experience_years(jd2),
                "graduation_years": join_semicolon(map(str, extract_graduation_years(jd2))),
                "is_target": is_target_role(jd2.splitlines()[0] if jd2 else ""),
            }
            result = match_job(fake, profile)
            st.metric("Match Score", f"{result['match_score']}/100")
            st.write("**匹配技能：**", result["matched_skills"] or "暂无")
            st.write("**缺口技能：**", result["missing_skills"] or "暂无")
            st.write("**资格/风险提示：**", result["eligibility_notes"] or "暂无明显硬性风险")

with tab5:
    st.markdown("""
### Pipeline
`Greenhouse API → Raw CSV → HTML Cleaning → Standardization → Requirement Extraction → SQLite → Matching → Streamlit`

### AI mode
- 无 API Key：本地规则提取 + 本地匹配全部可用。
- 有 `OPENAI_API_KEY`：额外启用 JD 深度分析。

### 注意
匹配分只是项目中的启发式功能，用来展示需求解析和候选人画像匹配思路，**不是录用概率预测**。
""")
    st.json(profile)
