from pathlib import Path

import pandas as pd

from joblens_core import normalize_company, normalize_job_title, normalize_location

INPUT = Path("data/processed/greenhouse_jobs_clean.csv")
OUTPUT = Path("data/processed/greenhouse_jobs_standardized.csv")


def main() -> None:
    df = pd.read_csv(INPUT)
    original_count = len(df)

    for col in ["company", "job_title", "location"]:
        raw_col = f"{col}_raw"
        if raw_col not in df.columns:
            df[raw_col] = df[col]

    df["company"] = df["company"].apply(normalize_company)
    df["job_title"] = df["job_title"].apply(normalize_job_title)
    df["location"] = df["location"].apply(normalize_location)

    df["_updated_at_parsed"] = pd.to_datetime(df.get("updated_at"), errors="coerce", utc=True)
    df = df.sort_values("_updated_at_parsed", ascending=False, na_position="last")

    url_dupes = int(df.duplicated(subset=["source_url"], keep="first").sum())
    df = df.drop_duplicates(subset=["source_url"], keep="first")

    key = ["company", "job_title", "location"]
    key_dupes = int(df.duplicated(subset=key, keep="first").sum())
    df = df.drop_duplicates(subset=key, keep="first")

    df = df.drop(columns=["_updated_at_parsed"]).reset_index(drop=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

    print(f"原始数据：{original_count}")
    print(f"source_url 重复：{url_dupes}")
    print(f"公司+岗位+地点重复：{key_dupes}")
    print(f"✅ 标准化并去重：{len(df)} 条 -> {OUTPUT}")


if __name__ == "__main__":
    main()
