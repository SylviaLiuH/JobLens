import pandas as pd
from bs4 import BeautifulSoup
import html
import re


# ==========================================
# 1. 读取原始 Greenhouse 岗位数据
# ==========================================
input_path = "data/raw/greenhouse_china_jobs.csv"

df = pd.read_csv(input_path)

print("原始数据条数：", len(df))


# ==========================================
# 2. HTML 清洗函数
# ==========================================
def clean_html_text(text):

    # 如果是空值，直接返回空字符串
    if pd.isna(text):
        return ""

    # 第一步：
    # 把 &lt; &gt; &amp; 等 HTML 转义字符还原
    text = html.unescape(text)

    # 第二步：
    # 使用 BeautifulSoup 去掉 HTML 标签
    soup = BeautifulSoup(text, "html.parser")

    # separator="\n"：
    # 不同 HTML 块之间用换行分隔
    text = soup.get_text(separator="\n")

    # 第三步：
    # 再解码一次可能残留的 HTML entity
    text = html.unescape(text)

    # 第四步：
    # 去掉每一行首尾空格
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    # 第五步：
    # 把连续很多空格压缩成一个空格
    cleaned_lines = []

    for line in lines:
        line = re.sub(r"\s+", " ", line)
        cleaned_lines.append(line)

    # 最终重新拼成正常文本
    return "\n".join(cleaned_lines)


# ==========================================
# 3. 清洗 description_html
# ==========================================
df["description_text"] = df["description_html"].apply(
    clean_html_text
)


# ==========================================
# 4. 检查清洗结果
# ==========================================
print("\n====================")
print("第一条岗位：", df.iloc[0]["job_title"])

print("\n--- 原始 HTML 前 500 字符 ---")
print(
    str(df.iloc[0]["description_html"])[:500]
)

print("\n--- 清洗后文本前 500 字符 ---")
print(
    df.iloc[0]["description_text"][:500]
)


# ==========================================
# 5. 简单数据质量检查
# ==========================================
print("\n====================")

print(
    "description_html 空值数量：",
    df["description_html"].isna().sum()
)

print(
    "description_text 空文本数量：",
    (df["description_text"].str.len() == 0).sum()
)

print(
    "平均 JD 文本长度：",
    round(df["description_text"].str.len().mean())
)


# ==========================================
# 6. 保存 processed 数据
# ==========================================
output_path = (
    "data/processed/greenhouse_jobs_clean.csv"
)

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 7. 完成提示
# ==========================================
print("\n====================")
print("✅ JD HTML 清洗完成")
print("清洗后数据条数：", len(df))
print("文件已保存到：", output_path)