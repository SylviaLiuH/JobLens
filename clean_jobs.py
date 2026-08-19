from pathlib import Path

import pandas as pd

from joblens_core import clean_html_text

INPUT = Path("data/raw/greenhouse_china_jobs.csv")
OUTPUT = Path("data/processed/greenhouse_jobs_clean.csv")


def main() -> None:
    df = pd.read_csv(INPUT)
    df["description_text"] = df["description_html"].apply(clean_html_text)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"✅ 清洗完成：{len(df)} 条 -> {OUTPUT}")


if __name__ == "__main__":
    main()
