from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from joblens_core import split_semicolon

INPUT = Path("data/processed/jobs_with_matches.csv")
FIG_DIR = Path("outputs/figures")
TABLE_DIR = Path("outputs/tables")
INSIGHTS = Path("outputs/insights.md")


def save_bar(series: pd.Series, title: str, xlabel: str, output: Path, top_n: int = 12) -> None:
    values = series.head(top_n).sort_values()
    plt.figure(figsize=(9, 5))
    values.plot(kind="barh")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(output, dpi=180)
    plt.close()


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)

    company_counts = df["company"].value_counts()
    category_counts = df["category"].value_counts()
    location_counts = df["location"].value_counts()
    skill_counter = Counter()
    for value in df["skills"].fillna(""):
        skill_counter.update(split_semicolon(value))
    skill_counts = pd.Series(skill_counter).sort_values(ascending=False)

    company_counts.rename_axis("company").rename("count").reset_index().to_csv(TABLE_DIR / "company_counts.csv", index=False, encoding="utf-8-sig")
    category_counts.rename_axis("category").rename("count").reset_index().to_csv(TABLE_DIR / "category_counts.csv", index=False, encoding="utf-8-sig")
    location_counts.rename_axis("location").rename("count").reset_index().to_csv(TABLE_DIR / "location_counts.csv", index=False, encoding="utf-8-sig")
    skill_counts.rename_axis("skill").rename("count").reset_index().to_csv(TABLE_DIR / "skill_counts.csv", index=False, encoding="utf-8-sig")

    save_bar(company_counts, "Jobs by Company", "Job count", FIG_DIR / "company_distribution.png")
    save_bar(category_counts, "Jobs by Category", "Job count", FIG_DIR / "category_distribution.png")
    save_bar(location_counts, "Jobs by Location", "Job count", FIG_DIR / "location_distribution.png")
    save_bar(skill_counts, "Top Skills Mentioned in JDs", "Mention count", FIG_DIR / "top_skills.png")

    target_count = int(df["is_target"].fillna(False).astype(bool).sum())
    top_match = df.iloc[0] if len(df) else None
    insight_lines = [
        "# JobLens Insights",
        "",
        f"- Unique China job records: **{len(df)}**",
        f"- Companies represented: **{df['company'].nunique()}**",
        f"- Target intern/graduate roles: **{target_count}**",
        f"- Most common location: **{location_counts.index[0] if len(location_counts) else 'N/A'}**",
        f"- Most common category: **{category_counts.index[0] if len(category_counts) else 'N/A'}**",
        f"- Most frequently mentioned skill: **{skill_counts.index[0] if len(skill_counts) else 'N/A'}**",
    ]
    if top_match is not None:
        insight_lines += [
            f"- Highest local match score: **{int(top_match['match_score'])}/100** — {top_match['company']} / {top_match['job_title']}",
            "",
            "> Match scores are heuristic portfolio features, not hiring predictions.",
        ]
    INSIGHTS.write_text("\n".join(insight_lines), encoding="utf-8")
    print(f"✅ 分析输出完成：{FIG_DIR} / {TABLE_DIR} / {INSIGHTS}")


if __name__ == "__main__":
    main()
