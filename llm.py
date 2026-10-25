# -*- coding: utf-8 -*-
"""
LLM 调用封装 — 兼容 OpenAI SDK（默认 DeepSeek）
学生可修改默认 base_url / model；API Key 也可通过环境变量注入。
"""

from __future__ import annotations

import os
from typing import Generator, Iterable, List, Dict, Optional

from openai import OpenAI

# ---------------------------------------------------------------------------
# 默认配置（F1 配置区可在 UI 中覆盖）
# ---------------------------------------------------------------------------
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"


def resolve_api_key(ui_key: str = "") -> str:
    """优先使用界面填写的 Key，其次环境变量。"""
    key = (ui_key or "").strip()
    if key:
        return key
    return (
        os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    ).strip()


def make_client(api_key: str, base_url: str) -> OpenAI:
    """创建 OpenAI 兼容客户端。"""
    if not api_key:
        raise ValueError(
            "未配置 API Key。请在侧边栏填写，或设置环境变量 "
            "DEEPSEEK_API_KEY / OPENAI_API_KEY。"
        )
    return OpenAI(api_key=api_key, base_url=base_url.rstrip("/") or DEFAULT_BASE_URL)


def chat_once(
    messages: List[Dict[str, str]],
    *,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
) -> str:
    """非流式单次对话，返回完整文本。"""
    client = make_client(api_key, base_url)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        raise RuntimeError(_friendly_error(e)) from e


def chat_stream(
    messages: List[Dict[str, str]],
    *,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.5,
) -> Generator[str, None, None]:
    """流式输出，逐块 yield 文本。"""
    client = make_client(api_key, base_url)
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
    except Exception as e:
        raise RuntimeError(_friendly_error(e)) from e


def _friendly_error(exc: Exception) -> str:
    """将常见异常转为中文友好提示。"""
    msg = str(exc)
    low = msg.lower()
    if "api key" in low or "authentication" in low or "401" in low:
        return "API Key 无效或未授权，请检查侧边栏配置或环境变量。"
    if "connection" in low or "timeout" in low or "network" in low:
        return f"网络连接失败，请检查网络或 base_url。详情：{msg}"
    if "404" in low or "not found" in low:
        return f"模型或接口地址可能不正确，请检查 model / base_url。详情：{msg}"
    return f"调用模型失败：{msg}"


# ---------------------------------------------------------------------------
# 业务 Prompt 构建（对应 F2 / F3 / F4 / F6 / F7）
# ---------------------------------------------------------------------------

def build_match_messages(resume: str, jd: str, knowledge: str) -> List[Dict[str, str]]:
    """F2 — 简历与 JD 匹配分析。"""
    system = (
        "你是制药行业资深招聘顾问与质量体系专家。"
        "请基于岗位 JD、候选人简历，并结合提供的 GMP/CMC/验证知识，"
        "给出结构化匹配分析。必须严格按以下格式开头（便于 UI 解析），然后再给详细 Markdown：\n"
        "SCORE: <0-100 整数>\n"
        "STATUS: <Good Match|Fair Match|Weak Match 之一>\n"
        "SUMMARY: <一句英文或中文总结>\n"
        "GAPS:\n"
        "- [Medium] <缺口描述>\n"
        "- [Low] <缺口描述>\n"
        "- [High] <可选，严重缺口>\n"
        "---\n"
        "然后输出详细分析：优势匹配点、缺口与风险、补强建议、建议面试考察主题。"
        "语气专业、简洁，适合课程演示。"
    )
    user = (
        f"【岗位 JD】\n{jd or '（未提供）'}\n\n"
        f"【候选人简历】\n{resume or '（未提供）'}\n\n"
        f"【制药知识参考】\n{knowledge[:6000]}\n"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_question_messages(
    resume: str, jd: str, knowledge: str, n: int = 5
) -> List[Dict[str, str]]:
    """F3 — 生成面试题。"""
    system = (
        "你是制药行业面试出题专家。请生成适合该候选人与岗位的面试题。"
        f"共 {n} 题，须覆盖：技术题、情景题、GMP 相关、CMC/法规相关（可多题）。"
        "严格按以下 Markdown 格式输出，不要多余前言：\n"
        "### Q1. 题干\n"
        "- 类型：技术/情景/GMP/CMC\n"
        "- 考察点：...\n"
        "- 参考要点：...\n"
        "### Q2. ...\n"
        "题目应紧扣 GMP/CMC/验证与岗位职责，难度适中，适合课程作业演示。"
    )
    user = (
        f"【岗位 JD】\n{jd or '（未提供）'}\n\n"
        f"【候选人简历】\n{resume or '（未提供）'}\n\n"
        f"【制药知识参考】\n{knowledge[:6000]}\n"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_score_messages(
    question: str, answer: str, knowledge: str
) -> List[Dict[str, str]]:
    """F4 — 单题评分。"""
    system = (
        "你是制药行业面试评分官。根据题目、考生作答与知识要点打分。"
        "输出 Markdown，包含：\n"
        "- 分数：x/10\n"
        "- 评语：...\n"
        "- 已掌握要点：...\n"
        "- 缺漏/不准确处：...\n"
        "- 改进建议：...\n"
        "评分要公正、具体，引用知识概念时用中文术语。"
    )
    user = (
        f"【题目】\n{question}\n\n"
        f"【考生作答】\n{answer}\n\n"
        f"【知识要点】\n{knowledge[:5000]}\n"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_report_messages(
    resume: str,
    jd: str,
    match_text: str,
    questions_text: str,
    scores: Iterable[str],
    interview_summary: str,
) -> List[Dict[str, str]]:
    """F6 — 面试复盘报告。"""
    scores_blob = "\n\n".join(s for s in scores if s) or "（暂无单题评分）"
    system = (
        "你是制药行业职业发展教练。请汇总本轮 AI 面试结果，生成「面试复盘报告」。"
        "使用清晰 Markdown 结构：总评、分项表现、知识短板、行动改进清单、一句话寄语。"
        "语气鼓励但客观，适合学生课后复盘。"
    )
    user = (
        f"【JD 摘要】\n{(jd or '')[:2000]}\n\n"
        f"【简历摘要】\n{(resume or '')[:2000]}\n\n"
        f"【匹配分析】\n{(match_text or '')[:3000]}\n\n"
        f"【面试题】\n{(questions_text or '')[:3000]}\n\n"
        f"【单题评分】\n{scores_blob[:4000]}\n\n"
        f"【虚拟面试对话摘要/总评素材】\n{(interview_summary or '')[:4000]}\n"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_interviewer_system(
    resume: str, jd: str, knowledge: str, focus_question: str = ""
) -> str:
    """F7 — 虚拟面试官系统提示。"""
    focus = (
        f"本轮重点围绕以下题目展开追问（建议 3-5 轮深入）：\n{focus_question}\n"
        if focus_question.strip()
        else "请从岗位与 GMP/CMC/验证相关主题中选择合适切入点开始面试。\n"
    )
    return (
        "你是「制药行业 AI 面试助手」中的虚拟面试官。"
        "身份：资深 QA/CMC/验证方向面试官，专业、礼貌、追问具体。"
        "规则：\n"
        "1. 每次只问一个问题或一个追问，长度适中；\n"
        "2. 依据候选人回答继续深挖细节、合规理解与实际案例；\n"
        "3. 可适度引用 GMP/偏差/CAPA/确认验证等概念考察；\n"
        "4. 不要一次性抛出很多问题；不要替候选人作答；\n"
        "5. 使用中文。\n\n"
        f"{focus}\n"
        f"【岗位 JD】\n{(jd or '未提供')[:2500]}\n\n"
        f"【候选人简历】\n{(resume or '未提供')[:2500]}\n\n"
        f"【知识库摘录】\n{knowledge[:4500]}\n"
    )


def build_final_eval_messages(
    transcript: List[Dict[str, str]], knowledge: str
) -> List[Dict[str, str]]:
    """F7 结束面试 → 综合总评（同时服务 F4/F6）。"""
    lines = []
    for m in transcript:
        role = "面试官" if m["role"] == "assistant" else "候选人"
        lines.append(f"{role}：{m['content']}")
    dialog = "\n".join(lines)
    system = (
        "你是制药行业资深面试官。请根据完整面试对话给出综合总评。"
        "输出 Markdown，包含：\n"
        "## 综合得分（0-100）\n"
        "## 维度评价（专业知识 / 合规意识 / 表达与逻辑 / 实践经验）\n"
        "## 亮点\n"
        "## 不足与风险\n"
        "## 录用建议倾向（仅供课程演示）\n"
        "## 学习改进清单\n"
        "评价需具体，可引用对话中的表述。"
    )
    user = f"【面试对话】\n{dialog[:8000]}\n\n【知识参考】\n{knowledge[:3000]}\n"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
