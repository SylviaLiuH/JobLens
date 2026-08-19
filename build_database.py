from pathlib import Path
import sqlite3

import pandas as pd

INPUT = Path("data/processed/greenhouse_jobs_structured.csv")
DB_PATH = Path("data/joblens.db")


def main() -> None:
    df = pd.read_csv(INPUT)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("jobs", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category)")
    print(f"✅ SQLite 数据库已生成：{DB_PATH} | jobs={len(df)}")


if __name__ == "__main__":
    main()
