import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/raw/jobs.csv")

print(df[["company", "job_title", "category"]].to_string(index=False))

print("\n各字段缺失值数量：")
print(df.isna().sum())

clean_df = df.copy()

clean_df = clean_df.fillna("Not specified")

clean_df.to_csv(
    "data/processed/jobs_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n清洗后的数据已保存！")

skills = (
    clean_df["skills"]
    .str.split(";")
    .explode()
    .str.strip()
)

skill_counts = skills.value_counts()

print("\n技能出现次数：")
print(skill_counts)

category_counts = clean_df["category"].value_counts()
print("\n岗位类别统计：")
print(category_counts)  

def normalize_category(category):
    if "AI" in category:
        return "AI"
    elif "Data" in category:
        return "Data"
    elif "Solution" in category or "Support" in category:
        return "Solution"
    elif "UX" in category or "Product" in category:
        return "Product/UX"
    else:
        return "Other"


def normalize_skill(skill):
    skill = skill.strip()

    if skill in ["AI", "GenAI"]:
        return "AI"
    else:
        return skill

normalized_skills = skills.apply(normalize_skill)

normalized_skill_counts = normalized_skills.value_counts()

print("\n标准化后的技能统计：")
print(normalized_skill_counts)
    
clean_df["main_category"] = clean_df["category"].apply(normalize_category)

print("\n标准化后的岗位类别：")
print(clean_df[["category", "main_category"]])

main_category_counts = clean_df["main_category"].value_counts()

print("\n标准化后的岗位类别统计：")
print(main_category_counts)

main_category_counts.plot(kind="bar")

plt.title("Job Category Distribution")
plt.xlabel("Category")
plt.ylabel("Number of Jobs")
plt.tight_layout()

plt.savefig(
    "outputs/figures/job_category_distribution.png",
    dpi=300
)

plt.close()

top_skills = normalized_skill_counts.head(10)

top_skills.plot(kind="bar")

plt.title("Top 10 Required Skills")
plt.xlabel("Skill")
plt.ylabel("Frequency")
plt.tight_layout()

plt.savefig(
    "outputs/figures/top_10_skills.png",
    dpi=300
)

plt.close()
