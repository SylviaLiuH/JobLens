from __future__ import annotations

import html
import re
from typing import Iterable

import pandas as pd
from bs4 import BeautifulSoup

CHINA_CITIES = [
    "Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Hangzhou",
    "Chengdu", "Suzhou", "Nanjing", "Wuhan", "Xi'an", "Tianjin",
    "Chongqing", "Xiamen", "Dalian", "Qingdao",
]

COMPANY_MAPPING = {
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
    "appier": "Appier",
}

SKILL_PATTERNS = {
    "Python": [r"\bpython\b"],
    "SQL": [r"\bsql\b"],
    "Java": [r"\bjava\b"],
    "C++": [r"\bc\+\+\b"],
    "C#": [r"\bc#\b", r"\bc sharp\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b"],
    "Go": [r"\bgolang\b", r"\bgo language\b"],
    "R": [r"\br language\b", r"\bprogramming in r\b"],
    "Excel": [r"\bexcel\b"],
    "Power BI": [r"\bpower\s*bi\b"],
    "Tableau": [r"\btableau\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Scikit-learn": [r"\bscikit[- ]?learn\b", r"\bsklearn\b"],
    "PyTorch": [r"\bpytorch\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "Deep Learning": [r"\bdeep learning\b"],
    "NLP": [r"\bnlp\b", r"natural language processing"],
    "Generative AI": [r"generative ai", r"\bgenai\b"],
    "LLM": [r"\bllms?\b", r"large language model"],
    "RAG": [r"\brag\b", r"retrieval[- ]augmented generation"],
    "LangChain": [r"\blangchain\b"],
    "Prompt Engineering": [r"prompt engineering"],
    "Agentic AI": [r"agentic ai", r"ai agents?"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"amazon web services"],
    "Azure": [r"\bazure\b"],
    "GCP": [r"\bgcp\b", r"google cloud"],
    "Cloud": [r"cloud computing", r"cloud[- ]native"],
    "Spark": [r"\bapache spark\b", r"\bspark\b"],
    "Kafka": [r"\bkafka\b"],
    "Git": [r"\bgit\b", r"github"],
    "Linux": [r"\blinux\b", r"\bunix\b"],
    "MongoDB": [r"\bmongodb\b"],
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "MySQL": [r"\bmysql\b"],
    "REST API": [r"\brest(?:ful)? api\b", r"\bapis?\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Streamlit": [r"\bstreamlit\b"],
    "JSON": [r"\bjson\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "React": [r"\breact(?:\.js)?\b"],
    "Node.js": [r"\bnode(?:\.js)?\b"],
    "Figma": [r"\bfigma\b"],
    "Data Analysis": [r"data analy(?:sis|tics)", r"analytical skills"],
    "Data Visualization": [r"data visuali[sz]ation", r"dashboard"],
    "Data Engineering": [r"data engineering"],
    "DevOps": [r"\bdevops\b"],
    "CI/CD": [r"\bci\s*/\s*cd\b", r"continuous integration"],
}


def clean_html_text(text: object) -> str:
    if pd.isna(text):
        return ""
    value = html.unescape(str(text))
    soup = BeautifulSoup(value, "html.parser")
    value = html.unescape(soup.get_text(separator="\n"))
    lines = []
    for line in value.splitlines():
        line = re.sub(r"\s+", " ", line.strip())
        if line:
            lines.append(line)
    return "\n".join(lines)


def normalize_company(company: object) -> str:
    if pd.isna(company):
        return ""
    value = re.sub(r"\s+", " ", str(company).strip())
    return COMPANY_MAPPING.get(value.lower(), value)


def normalize_job_title(title: object) -> str:
    if pd.isna(title):
        return ""
    value = html.unescape(str(title))
    value = value.replace("–", "-").replace("—", "-").replace("‑", "-")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def normalize_location(location: object) -> str:
    if pd.isna(location):
        return ""
    value = re.sub(r"\s+", " ", str(location).strip())
    lower = value.lower()
    found = [city for city in CHINA_CITIES if city.lower() in lower]
    if found:
        out = "; ".join(dict.fromkeys(found))
        if "remote" in lower:
            out += "; Remote"
        return out
    if "china" in lower:
        return "China; Remote" if "remote" in lower else "China"
    return value


def is_china_location(location: object) -> bool:
    if pd.isna(location):
        return False
    lower = str(location).lower()
    return "china" in lower or any(city.lower() in lower for city in CHINA_CITIES)


def is_target_role(title: object) -> bool:
    if pd.isna(title):
        return False
    lower = str(title).lower()
    keywords = [
        "intern", "internship", "graduate", "new grad", "entry level",
        "campus", "trainee",
    ]
    return any(keyword in lower for keyword in keywords)


def extract_skills(text: object) -> list[str]:
    if pd.isna(text):
        return []
    lower = str(text).lower()
    skills: list[str] = []
    for skill, patterns in SKILL_PATTERNS.items():
        if any(re.search(pattern, lower, flags=re.I) for pattern in patterns):
            skills.append(skill)
    return skills


def extract_education(text: object) -> str:
    if pd.isna(text):
        return "Not specified"

    lower = str(text).lower()

    # Bachelor + Master
    if re.search(
        r"bachelor'?s?(?:\s+degree)?\s+(?:or|/)\s+master'?s?(?:\s+degree)?",
        lower,
    ):
        return "Bachelor or Master"

    # Bachelor + Master + PhD
    if re.search(
        r"(?:bachelor|bs|b\.s\.|ba|b\.a\.).*?(?:master|ms|m\.s\.).*?(?:ph\.?d|doctoral|doctorate)",
        lower,
    ):
        return "Bachelor / Master / PhD"

    # Master + PhD
    if re.search(
        r"master'?s?(?:\s+degree)?\s+(?:or|/)\s+ph\.?d|"
        r"ms\s*/\s*phd|m\.s\.\s*/\s*ph\.d",
        lower,
    ):
        return "Master or PhD"

    # PhD only
    if re.search(r"\bph\.?d\.?\b|doctoral|doctorate", lower):
        return "PhD"

    # Master only
    if re.search(
        r"master'?s?(?:\s+degree)?|\bm\.s\.\b|\bms degree\b",
        lower,
    ):
        return "Master"

    # Bachelor only
    if re.search(
        r"bachelor'?s?(?:\s+degree)?|\bba/bs\b|\bbs/ba\b|"
        r"\bb\.s\.\b|\bb\.a\.\b|undergraduate degree",
        lower,
    ):
        return "Bachelor"

    if re.search(r"college degree|university degree", lower):
        return "Bachelor/University"

    return "Not specified"


def extract_english_requirement(text: object) -> str:
    if pd.isna(text):
        return "Not specified"
    lower = str(text).lower()
    if not re.search(r"\benglish\b", lower):
        return "Not specified"
    if re.search(r"fluent|fluency|native[- ]level|excellent english|proficien", lower):
        return "Fluent/Professional"
    if re.search(r"english.*(?:required|must)|(?:required|must).*english", lower):
        return "Required"
    if re.search(r"english.*(?:preferred|plus)|(?:preferred|plus).*english", lower):
        return "Preferred"
    return "Mentioned"


def extract_experience_years(text: object) -> int | None:
    if pd.isna(text):
        return None
    lower = str(text).lower()
    matches = re.findall(r"(?<!\d)(\d{1,2})\s*\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:relevant\s+|related\s+|professional\s+|work\s+|industry\s+|field\s+)?experience", lower)
    if not matches:
        matches = re.findall(r"(?:at least|minimum(?: of)?)\s+(\d{1,2})\s*(?:years?|yrs?)", lower)
    if not matches:
        return None
    values = [int(x) for x in matches if int(x) <= 20]
    return max(values) if values else None


def extract_graduation_years(text: object) -> list[int]:
    if pd.isna(text):
        return []
    years: set[int] = set()
    for line in str(text).splitlines():
        lower = line.lower()
        if any(k in lower for k in ["graduat", "class of", "expected degree", "degree completion"]):
            for year in re.findall(r"\b20(?:2[5-9]|3[0-5])\b", line):
                years.add(int(year))
    return sorted(years)


def categorize_job(title: object, description: object = "") -> str:
    text = f"{title or ''} {description or ''}".lower()
    title_lower = str(title or "").lower()
    if any(k in title_lower for k in ["data scientist", "data science", "machine learning", "ai engineer", "artificial intelligence", "quantitative research"]):
        return "Data/AI"
    if any(k in title_lower for k in ["data analyst", "analytics", "business intelligence"]):
        return "Data/Analytics"
    if any(k in title_lower for k in ["solution architect", "solutions architect", "solution engineer", "technical account", "support engineer", "consultant"]):
        return "Solution/Support"
    if any(k in title_lower for k in ["product", "ux", "user experience", "designer"]):
        return "Product/UX"
    if any(k in title_lower for k in ["software", "developer", "engineer", "sre", "reliability", "backend", "frontend", "full stack", "cloud"]):
        return "Software/Cloud"
    if any(k in title_lower for k in ["account", "sales", "business development", "growth", "operations", "marketing"]):
        return "Business/Ops"
    if any(k in text for k in ["machine learning", "generative ai", "large language model"]):
        return "Data/AI"
    return "Other"


def degree_rank(value: str) -> int:
    lower = (value or "").lower()
    if "phd" in lower:
        return 3
    if "master" in lower:
        return 2
    if "bachelor" in lower or "university" in lower:
        return 1
    return 0


def split_semicolon(value: object) -> list[str]:
    if pd.isna(value) or str(value).strip() == "":
        return []
    return [x.strip() for x in str(value).split(";") if x.strip()]


def join_semicolon(items: Iterable[str]) -> str:
    return "; ".join(dict.fromkeys([x for x in items if x]))
