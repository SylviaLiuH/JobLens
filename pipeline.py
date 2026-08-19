from clean_jobs import main as clean_main
from standardize_jobs import main as standardize_main
from extract_requirements import main as extract_main
from build_database import main as db_main
from matcher import score_dataset
from analyze_jobs import main as analyze_main


def main() -> None:
    print("=== JobLens Pipeline ===")
    clean_main()
    standardize_main()
    extract_main()
    db_main()
    score_dataset()
    print("✅ 匹配评分完成")
    analyze_main()
    print("\n🎉 JobLens V1 数据流水线全部完成")


if __name__ == "__main__":
    main()
