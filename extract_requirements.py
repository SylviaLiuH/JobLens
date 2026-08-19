from pathlib import Path

import pandas as pd

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

INPUT = Path("data/processed/greenhouse_jobs_standardized.csv")
OUTPUT = Path("data/processed/greenhouse_jobs_structured.csv")


def main() -> None:
    df = pd.read_csv(INPUT)

    df["category"] = df.apply(lambda r: categorize_job(r.get("job_title", ""), r.get("description_text", "")), axis=1)
    df["skills"] = df["description_text"].apply(lambda x: join_semicolon(extract_skills(x)))
    df["education"] = df["description_text"].apply(extract_education)
    df["english_requirement"] = df["description_text"].apply(extract_english_requirement)
    df["experience_years"] = df["description_text"].apply(extract_experience_years)
    df["graduation_years"] = df["description_text"].apply(lambda x: join_semicolon(map(str, extract_graduation_years(x))))
    df["is_target"] = df["job_title"].apply(is_target_role)

    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"✅ 结构化提取完成：{len(df)} 条 -> {OUTPUT}")
    print("类别分布：")
    print(df["category"].value_counts())


if __name__ == "__main__":
    main()
