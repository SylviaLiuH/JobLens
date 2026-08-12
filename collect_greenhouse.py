import requests
import pandas as pd
from datetime import date


# ==========================================
# 1. 获取某家公司的 Greenhouse 岗位
# ==========================================
def fetch_jobs(board_token):
    url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board_token}/jobs?content=true"
    )

    response = requests.get(url, timeout=20)

    # 404 / 500 等错误直接抛出异常
    response.raise_for_status()

    data = response.json()

    return data["jobs"]


# ==========================================
# 2. 判断是否为中国相关岗位
# ==========================================
def is_china_job(job):
    location_name = job["location"]["name"].lower()

    china_keywords = [
        "china",
        "shanghai",
        "beijing",
        "shenzhen",
        "guangzhou",
        "hangzhou",
        "chengdu",
        "suzhou"
    ]

    return any(
        keyword in location_name
        for keyword in china_keywords
    )


# ==========================================
# 3. 判断是否为实习 / 应届岗位
# ==========================================
def is_target_job(job):
    title = job["title"].lower()

    target_keywords = [
        "intern",
        "internship",
        "graduate",
        "new grad",
        "entry level"
    ]

    return any(
        keyword in title
        for keyword in target_keywords
    )


# ==========================================
# 4. 把 Greenhouse 数据转换成 JobLens 格式
# ==========================================
def convert_job(company_name, board_token, job):
    return {
        "company": company_name,
        "board_token": board_token,
        "job_title": job["title"],
        "location": job["location"]["name"],
        "description_html": job.get("content", ""),
        "source_url": job["absolute_url"],
        "first_published": job.get("first_published", ""),
        "updated_at": job.get("updated_at", ""),
        "is_target": is_target_job(job),
        "source_type": "greenhouse_api",
        "date_collected": date.today().isoformat()
    }


# ==========================================
# 5. 从配置文件读取公司
# ==========================================
companies_df = pd.read_csv(
    "config/greenhouse_companies.csv"
)

print("配置文件中公司数量：", len(companies_df))


# ==========================================
# 6. 准备存放最终数据
# ==========================================
all_china_jobs = []

collection_summary = []


# ==========================================
# 7. 批量采集
# ==========================================
for _, row in companies_df.iterrows():

    company_name = row["company"]
    board_token = row["board_token"]

    print("\n================================")
    print("正在采集：", company_name)

    try:
        jobs = fetch_jobs(board_token)

    except requests.RequestException as error:
        print("❌ 采集失败：", error)

        collection_summary.append({
            "company": company_name,
            "board_token": board_token,
            "status": "failed",
            "total_jobs": 0,
            "china_jobs": 0,
            "target_jobs": 0
        })

        # 当前公司失败后，继续采下一家公司
        continue


    # 筛选中国岗位
    china_jobs = []

    for job in jobs:
        if is_china_job(job):
            china_jobs.append(job)


    # 筛选中国地区实习 / 应届岗位
    target_jobs = []

    for job in china_jobs:
        if is_target_job(job):
            target_jobs.append(job)


    print("岗位总数：", len(jobs))
    print("中国相关岗位：", len(china_jobs))
    print("中国实习/应届岗位：", len(target_jobs))


    # 保存中国岗位
    for job in china_jobs:

        record = convert_job(
            company_name,
            board_token,
            job
        )

        all_china_jobs.append(record)


    # 保存本次采集统计
    collection_summary.append({
        "company": company_name,
        "board_token": board_token,
        "status": "success",
        "total_jobs": len(jobs),
        "china_jobs": len(china_jobs),
        "target_jobs": len(target_jobs)
    })


# ==========================================
# 8. 转成 DataFrame
# ==========================================
jobs_df = pd.DataFrame(all_china_jobs)

summary_df = pd.DataFrame(collection_summary)


# ==========================================
# 9. 保存所有中国岗位
# ==========================================
jobs_output_path = (
    "data/raw/greenhouse_china_jobs.csv"
)

jobs_df.to_csv(
    jobs_output_path,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 10. 单独保存实习 / 应届岗位
# ==========================================
if len(jobs_df) > 0:

    target_df = jobs_df[
        jobs_df["is_target"] == True
    ]

else:
    target_df = pd.DataFrame()


target_output_path = (
    "data/raw/greenhouse_target_jobs.csv"
)

target_df.to_csv(
    target_output_path,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 11. 保存采集统计
# ==========================================
summary_output_path = (
    "data/raw/greenhouse_collection_summary.csv"
)

summary_df.to_csv(
    summary_output_path,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 12. 最终结果
# ==========================================
print("\n================================")
print("🎉 Greenhouse 数据采集完成")

print("成功采集公司数：",
      (summary_df["status"] == "success").sum())

print("失败公司数：",
      (summary_df["status"] == "failed").sum())

print("中国岗位总数：", len(jobs_df))

print("目标实习/应届岗位总数：",
      len(target_df))

print("\n文件已保存：")
print("-", jobs_output_path)
print("-", target_output_path)
print("-", summary_output_path)