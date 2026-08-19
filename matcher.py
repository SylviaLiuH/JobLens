from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from joblens_core import degree_rank, extract_skills, join_semicolon, split_semicolon

PROFILE_PATH = Path("config/candidate_profile.json")


def load_profile(path: Path = PROFILE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def match_job(row: pd.Series | dict, profile: dict) -> dict:
    get = row.get
    jd_skills = set(split_semicolon(get("skills", "")))
    profile_skills = set(profile.get("skills", []))
    matched = sorted(jd_skills & profile_skills)
    missing = sorted(jd_skills - profile_skills)

    if jd_skills:
        skill_score = 55 * len(matched) / len(jd_skills)
    else:
        # 没提取到明确技能时，不因为“信息缺失”给高分
        skill_score = 10

    required_degree = str(get("education", "Not specified"))
    candidate_degree = profile.get("education", "Bachelor")
    if required_degree == "Not specified":
        education_score = 15
    else:
        education_score = 15 if degree_rank(candidate_degree) >= degree_rank(required_degree) else 0

    english = str(get("english_requirement", "Not specified"))
    english_score = 10 if english == "Not specified" or profile.get("english_evidence") else 0

    is_target = bool(get("is_target", False))
    target_score = 20 if is_target else 0

    title_lower = str(get("job_title", "")).lower()
    seniority_penalty = 0
    if not is_target:
        if any(k in title_lower for k in ["senior", "sr ", "staff", "principal", "director", "head", "lead", "manager"]):
            seniority_penalty = 40
        else:
            seniority_penalty = 10

    experience_years = get("experience_years")
    experience_penalty = 0
    notes: list[str] = []
    try:
        exp = int(float(experience_years)) if pd.notna(experience_years) else None
    except (TypeError, ValueError):
        exp = None
    if exp is not None and exp >= 2:
        experience_penalty = min(30, 10 + exp * 3)
        notes.append(f"JD 明确要求约 {exp}+ 年经验")

    grad_years = [int(x) for x in split_semicolon(get("graduation_years", "")) if x.isdigit()]
    grad_penalty = 0
    candidate_year = int(profile.get("graduation_year", 0) or 0)
    if grad_years and candidate_year and candidate_year not in grad_years:
        grad_penalty = 15
        notes.append(f"JD 提到毕业年份 {grad_years}，你的毕业年份是 {candidate_year}")

    if degree_rank(candidate_degree) < degree_rank(required_degree):
        notes.append(f"学历要求为 {required_degree}，当前学历层级为 {candidate_degree}")

    if bool(get("is_target", False)) and profile.get("external_internship_policy") == "pending_confirmation":
        notes.append("校外长期实习政策仍需向学校确认")

    score = max(0, min(100, round(skill_score + education_score + english_score + target_score - seniority_penalty - experience_penalty - grad_penalty)))

    return {
        "match_score": score,
        "matched_skills": join_semicolon(matched),
        "missing_skills": join_semicolon(missing),
        "eligibility_notes": "；".join(notes),
    }


def score_dataset(input_path: str = "data/processed/greenhouse_jobs_structured.csv", output_path: str = "data/processed/jobs_with_matches.csv") -> pd.DataFrame:
    df = pd.read_csv(input_path)
    profile = load_profile()
    matches = df.apply(lambda row: pd.Series(match_job(row, profile)), axis=1)
    out = pd.concat([df, matches], axis=1)
    out = out.sort_values("match_score", ascending=False).reset_index(drop=True)
    out.to_csv(output_path, index=False, encoding="utf-8-sig")
    return out


if __name__ == "__main__":
    result = score_dataset()
    print("✅ 匹配评分完成")
    print(result[["company", "job_title", "match_score", "matched_skills", "missing_skills"]].head(10).to_string(index=False))
