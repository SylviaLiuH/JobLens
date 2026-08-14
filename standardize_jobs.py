import pandas as pd
import re
import html


# ==========================================
# 1. 文件路径
# ==========================================
input_path = "data/processed/greenhouse_jobs_clean.csv"
output_path = "data/processed/greenhouse_jobs_standardized.csv"


# ==========================================
# 2. 读取昨天清洗好的数据
# ==========================================
df = pd.read_csv(input_path)

print("原始数据条数：", len(df))


# ==========================================
# 3. 先保存原始字段
# ==========================================
# 以后如果标准化规则写错了，
# 仍然可以回头看到 API 原来的内容
df["company_raw"] = df["company"]
df["job_title_raw"] = df["job_title"]
df["location_raw"] = df["location"]


# ==========================================
# 4. 公司名称标准化
# ==========================================
company_mapping = {
    "mongodb": "MongoDB",
    "moloco": "Moloco",
    "the trade desk": "The Trade Desk",
    "flexport": "Flexport",
    "project44": "project44",
    "ses ai": "SES AI",
    "alphagrep securities": "AlphaGrep Securities",
    "worldquant": "WorldQuant",
    "speechify": "Speechify",
    "goat group": "GOAT Group",
    "appier": "Appier"
}


def normalize_company(company):
    # 空值直接返回空字符串
    if pd.isna(company):
        return ""

    # 去掉首尾空格
    company = str(company).strip()

    # 把连续多个空格压缩成一个
    company = re.sub(r"\s+", " ", company)

    # 转小写后查标准名称
    key = company.lower()

    return company_mapping.get(key, company)


df["company"] = df["company"].apply(
    normalize_company
)


# ==========================================
# 5. 岗位名称标准化
# ==========================================
def normalize_job_title(title):
    if pd.isna(title):
        return ""

    title = str(title)

    # HTML entity 解码
    title = html.unescape(title)

    # 把不同类型的破折号统一成普通 -
    title = title.replace("–", "-")
    title = title.replace("—", "-")
    title = title.replace("-", "-")

    # 连续空格 -> 一个空格
    title = re.sub(r"\s+", " ", title)

    # 去首尾空格
    title = title.strip()

    return title


df["job_title"] = df["job_title"].apply(
    normalize_job_title
)


# ==========================================
# 6. 工作地点标准化
# ==========================================

# 今天先覆盖我们比较常见的中国城市
city_names = [
    "Beijing",
    "Shanghai",
    "Shenzhen",
    "Guangzhou",
    "Hangzhou",
    "Chengdu",
    "Suzhou",
    "Nanjing",
    "Wuhan",
    "Xi'an",
    "Tianjin",
    "Chongqing",
    "Xiamen",
    "Dalian",
    "Qingdao"
]


def normalize_location(location):
    if pd.isna(location):
        return ""

    location = str(location).strip()

    # 清理连续空格
    location = re.sub(r"\s+", " ", location)

    location_lower = location.lower()

    found_cities = []

    # 找出地点中出现了哪些城市
    for city in city_names:
        if city.lower() in location_lower:
            found_cities.append(city)

    # 如果找到了城市
    if found_cities:
        result = "; ".join(found_cities)

        # 如果同时还是 Remote
        if "remote" in location_lower:
            result += "; Remote"

        return result

    # 没找到具体城市，但是明确是 China
    if "china" in location_lower:
        if "remote" in location_lower:
            return "China; Remote"

        return "China"

    # 实在识别不了就保留原值
    return location


df["location"] = df["location"].apply(
    normalize_location
)


# ==========================================
# 7. 基础缺失值检查
# ==========================================
print("\n====================")
print("标准化后的缺失情况")

print(
    "company 空值：",
    (df["company"] == "").sum()
)

print(
    "job_title 空值：",
    (df["job_title"] == "").sum()
)

print(
    "location 空值：",
    (df["location"] == "").sum()
)


# ==========================================
# 8. 准备去重
# ==========================================

# 把 updated_at 转成真正的时间类型
# 这样如果出现重复岗位，可以优先保留更新时间较新的
df["_updated_at_parsed"] = pd.to_datetime(
    df["updated_at"],
    errors="coerce",
    utc=True
)

df = df.sort_values(
    "_updated_at_parsed",
    ascending=False,
    na_position="last"
)


# ==========================================
# 9. 检查 source_url 完全重复
# ==========================================
url_duplicate_count = df.duplicated(
    subset=["source_url"],
    keep="first"
).sum()

print("\n完全重复 source_url 数量：",
      url_duplicate_count)


# 先根据 source_url 去重
df = df.drop_duplicates(
    subset=["source_url"],
    keep="first"
)


# ==========================================
# 10. 公司 + 岗位 + 地点 去重
# ==========================================
duplicate_key = [
    "company",
    "job_title",
    "location"
]

job_duplicate_count = df.duplicated(
    subset=duplicate_key,
    keep="first"
).sum()

print(
    "公司 + 岗位 + 地点重复数量：",
    job_duplicate_count
)


df = df.drop_duplicates(
    subset=duplicate_key,
    keep="first"
)


# ==========================================
# 11. 删除辅助时间列
# ==========================================
df = df.drop(
    columns=["_updated_at_parsed"]
)


# ==========================================
# 12. 重置索引
# ==========================================
df = df.reset_index(drop=True)


# ==========================================
# 13. 输出标准化结果
# ==========================================
print("\n====================")

print("标准化并去重后数据条数：",
      len(df))

print(
    "公司数量：",
    df["company"].nunique()
)

print(
    "岗位名称数量：",
    df["job_title"].nunique()
)


print("\n地点分布：")

print(
    df["location"]
    .value_counts()
    .head(15)
)


# ==========================================
# 14. 展示前几条数据检查
# ==========================================
print("\n====================")
print("标准化样例：")

print(
    df[
        [
            "company",
            "job_title",
            "location"
        ]
    ].head(10)
)


# ==========================================
# 15. 保存标准化数据
# ==========================================
df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 16. 完成
# ==========================================
print("\n====================")
print("✅ 岗位数据标准化完成")
print("文件已保存到：", output_path)