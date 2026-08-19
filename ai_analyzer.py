from __future__ import annotations

import json
import os


def analyze_jd_with_ai(jd_text: str, candidate_profile: dict) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "未检测到 OPENAI_API_KEY。当前仍可使用本地规则提取与匹配；配置 API Key 后可启用 AI 深度分析。"

    try:
        from openai import OpenAI
    except ImportError:
        return "未安装 openai 包，请先运行：pip install -r requirements.txt"

    model = os.getenv("OPENAI_MODEL", "gpt-5.6")
    client = OpenAI()
    prompt = f"""
你是一个求职 JD 分析助手。请基于 JD 和候选人画像，用中文给出简洁、证据化的分析。
不要虚构 JD 没有写的要求。输出以下五个小节：
1. 岗位概览
2. 关键要求
3. 候选人匹配点
4. 主要缺口/风险
5. 下一步建议（最多 5 条）

候选人画像：
{json.dumps(candidate_profile, ensure_ascii=False, indent=2)}

JD：
{jd_text[:12000]}
""".strip()

    response = client.responses.create(model=model, input=prompt)
    return response.output_text
