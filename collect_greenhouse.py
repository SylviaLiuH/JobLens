from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import requests

from joblens_core import is_china_location, is_target_role

CONFIG_PATH = Path("config/greenhouse_companies.csv")
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_jobs(board_token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()["jobs"]


def convert_job(company_name: str, board_token: str, job: dict) -> dict:
    location = job.get("location", {}).get("name", "")
    return {
        "company": company_name,
        "board_token": board_token,
        "job_title": job.get("title", ""),
        "location": location,
        "description_html": job.get("content", ""),
        "source_url": job.get("absolute_url", ""),
        "first_published": job.get("first_published", ""),
        "updated_at": job.get("updated_at", ""),
        "is_target": is_target_role(job.get("title", "")),
        "source_type": "greenhouse_api",
        "date_collected": date.today().isoformat(),
    }


def main() -> None:
    companies = pd.read_csv(CONFIG_PATH)
    all_china_jobs: list[dict] = []
    summary: list[dict] = []

    print(f"配置公司数量：{len(companies)}")

    for _, row in companies.iterrows():
        company = row["company"]
        token = row["board_token"]
        print(f"\n正在采集：{company}")
        try:
            jobs = fetch_jobs(token)
            china_jobs = [job for job in jobs if is_china_location(job.get("location", {}).get("name", ""))]
            target_jobs = [job for job in china_jobs if is_target_role(job.get("title", ""))]
            all_china_jobs.extend(convert_job(company, token, job) for job in china_jobs)
            summary.append({
                "company": company,
                "board_token": token,
                "status": "success",
                "total_jobs": len(jobs),
                "china_jobs": len(china_jobs),
                "target_jobs": len(target_jobs),
            })
            print(f"岗位总数：{len(jobs)} | 中国岗位：{len(china_jobs)} | 实习/应届：{len(target_jobs)}")
        except requests.RequestException as exc:
            print(f"❌ 采集失败：{exc}")
            summary.append({
                "company": company,
                "board_token": token,
                "status": "failed",
                "total_jobs": 0,
                "china_jobs": 0,
                "target_jobs": 0,
            })

    jobs_df = pd.DataFrame(all_china_jobs)
    summary_df = pd.DataFrame(summary)
    target_df = jobs_df[jobs_df["is_target"] == True].copy() if not jobs_df.empty else pd.DataFrame()

    jobs_df.to_csv(RAW_DIR / "greenhouse_china_jobs.csv", index=False, encoding="utf-8-sig")
    target_df.to_csv(RAW_DIR / "greenhouse_target_jobs.csv", index=False, encoding="utf-8-sig")
    summary_df.to_csv(RAW_DIR / "greenhouse_collection_summary.csv", index=False, encoding="utf-8-sig")

    print("\n✅ Greenhouse 数据采集完成")
    print(f"中国岗位总数：{len(jobs_df)}")
    print(f"目标岗位总数：{len(target_df)}")


if __name__ == "__main__":
    main()
