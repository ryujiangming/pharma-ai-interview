# -*- coding: utf-8 -*-
"""
制药行业 AI 面试助手 — 课程作业 Streamlit 应用
================================================
验收主流程：
  输入简历+JD（F1）→ 匹配结果（F2）→ 生成面试题（F3）
  → 虚拟面试官多轮问答（F7）→ 结束并评价/评分（F4 / F6）

功能标签与 URS 对齐：
  F1  资料输入（粘贴 / 上传 PDF·TXT）
  F2  简历与 JD 匹配分析
  F3  生成面试题
  F4  作答评分 / 综合评分
  F5  内置 GMP/CMC/验证知识（可补充上传）
  F6  结果清晰展示与面试复盘报告
  F7  虚拟面试官多轮问答（重点，建议每题 3–5 轮）

UI：贴近 Apple 风格 mockup — 双栏卡片、钢蓝强调色、大留白。
技术：OpenAI 兼容 API（默认 DeepSeek），单用户本地演示。
"""

from __future__ import annotations

import io
import re
from typing import List, Optional, Tuple

import streamlit as st
from pypdf import PdfReader

import knowledge
import llm
import styles

# ---------------------------------------------------------------------------
# 页面基础
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Pharma Interview Assistant · 制药行业 AI 面试助手",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

styles.inject_styles()


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def extract_text_from_upload(uploaded) -> str:
    """从 PDF / TXT 提取文本。"""
    if uploaded is None:
        return ""
    name = (uploaded.name or "").lower()
    raw = uploaded.read()
    try:
        if name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(raw))
            return "\n".join((p.extract_text() or "") for p in reader.pages).strip()
        for enc in ("utf-8", "gbk", "latin-1"):
            try:
                return raw.decode(enc).strip()
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        st.warning(f"文件解析失败（{uploaded.name}）：{e}")
        return ""


def format_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def merged_knowledge() -> str:
    """F5：内置知识 + 用户补充材料。"""
    extra = st.session_state.get("extra_knowledge", "") or ""
    if extra.strip():
        return knowledge.BUILTIN_KNOWLEDGE + "\n\n【用户补充知识】\n" + extra.strip()
    return knowledge.BUILTIN_KNOWLEDGE


def require_key() -> Optional[str]:
    key = llm.resolve_api_key(st.session_state.get("api_key", ""))
    if not key:
        st.error(
            "尚未配置 API Key。请在左侧「API 配置」填写，"
            "或设置环境变量 DEEPSEEK_API_KEY / OPENAI_API_KEY。"
        )
        return None
    return key


def parse_match_score(text: str) -> Optional[int]:
    """从模型输出解析 0–100 匹配分。"""
    if not text:
        return None
    patterns = [
        r"SCORE\s*[:：]\s*(\d{1,3})",
        r"匹配度[^\d]{0,12}(\d{1,3})\s*%?",
        r"总分[^\d]{0,12}(\d{1,3})",
        r"(\d{1,3})\s*/\s*100",
        r"(\d{1,3})\s*%",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 0 <= val <= 100:
                return val
    return None


def parse_match_status(text: str, score: Optional[int]) -> str:
    m = re.search(r"STATUS\s*[:：]\s*(.+)", text or "", flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().splitlines()[0][:40]
    if score is None:
        return "待分析"
    if score >= 75:
        return "Good Match"
    if score >= 55:
        return "Fair Match"
    return "Weak Match"


def parse_match_summary(text: str) -> str:
    m = re.search(r"SUMMARY\s*[:：]\s*(.+)", text or "", flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().splitlines()[0][:160]
    if not text:
        return "上传简历与 JD 后，点击下方按钮生成匹配分析。"
    # 取首段非结构化短句
    for line in text.splitlines():
        line = line.strip().lstrip("#*- ")
        if len(line) > 20 and not line.upper().startswith(("SCORE", "STATUS", "GAPS", "SUMMARY")):
            return line[:160]
    return "背景整体有一定吻合度，详见下方缺口与完整分析。"


def parse_gaps(text: str) -> List[Tuple[str, str]]:
    """解析缺口条目 → (描述, high|medium|low)。"""
    gaps: List[Tuple[str, str]] = []
    if not text:
        return gaps
    # 结构化 [Medium] / [Low] / [High]
    for m in re.finditer(
        r"[-*]\s*\[(High|Medium|Low)\]\s*(.+)",
        text,
        flags=re.IGNORECASE,
    ):
        level = m.group(1).lower()
        desc = m.group(2).strip()[:90]
        if desc:
            gaps.append((desc, level))
    if gaps:
        return gaps[:5]

    # 回退：在「缺口」小节抓列表项
    section = re.search(
        r"(缺口|风险|不足|Gaps?)[\s\S]{0,800}",
        text,
        flags=re.IGNORECASE,
    )
    blob = section.group(0) if section else text
    for m in re.finditer(r"[-*]\s+(.+)", blob):
        desc = m.group(1).strip()[:90]
        if len(desc) < 6:
            continue
        low = desc.lower()
        if any(k in low for k in ("严重", "high", "关键缺失")):
            level = "high"
        elif any(k in low for k in ("轻微", "low", "较少")):
            level = "low"
        else:
            level = "medium"
        gaps.append((desc, level))
        if len(gaps) >= 4:
            break
    return gaps


def parse_questions(text: str) -> List[str]:
    """从 F3 输出解析题干列表。"""
    if not text:
        return []
    qs: List[str] = []
    # ### Q1. 题干  或  ### 1. 题干
    for m in re.finditer(
        r"^#{1,3}\s*Q?\s*\d+[\.、:：\s]+(.+)$",
        text,
        flags=re.MULTILINE,
    ):
        q = m.group(1).strip()
        if q:
            qs.append(q)
    if qs:
        return qs
    # 1. 题干
    for m in re.finditer(r"^\s*\d+[\.、]\s+(.+)$", text, flags=re.MULTILINE):
        q = m.group(1).strip()
        if len(q) > 8:
            qs.append(q)
    return qs[:10]


def init_state():
    defaults = {
        "api_key": "",
        "base_url": llm.DEFAULT_BASE_URL,
        "model": llm.DEFAULT_MODEL,
        "resume_text": "",
        "jd_text": "",
        "resume_filename": "",
        "resume_filesize": 0,
        "extra_knowledge": "",
        "match_result": "",
        "questions_result": "",
        "score_results": [],
        "report_result": "",
        "interview_messages": [],
        "interview_started": False,
        "focus_question": "",
        "final_eval": "",
        "practice_answer": "",
        "practice_score": "",
        "show_score_panel": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ---------------------------------------------------------------------------
# 侧边栏：简要说明（API 在主区顶部展开；F5 在左栏卡片）
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### 说明")
    st.caption(
        "API Key / Base URL / Model → 请使用主区顶部「API 配置」展开面板。"
        " F5 内置知识在「准备与出题」左栏可见，无需打开本侧边栏。"
    )
    st.markdown("---")
    st.caption("也可设置环境变量 DEEPSEEK_API_KEY 或 OPENAI_API_KEY。")


# ---------------------------------------------------------------------------
# Header + 主区 API 展开（不依赖侧边栏）
# ---------------------------------------------------------------------------
styles.render_header()

with st.expander("⚙️ API 配置（Key / Base URL / Model）", expanded=False):
    st.caption("兼容 OpenAI SDK · 默认 DeepSeek；也可设置环境变量 DEEPSEEK_API_KEY")
    c_a, c_b, c_c = st.columns(3)
    with c_a:
        st.session_state.api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-… 或留空用环境变量",
            key="api_key_main",
        )
    with c_b:
        st.session_state.base_url = st.text_input(
            "Base URL",
            value=st.session_state.base_url,
            key="base_url_main",
        )
    with c_c:
        st.session_state.model = st.text_input(
            "Model",
            value=st.session_state.model,
            key="model_main",
        )

tab_prep, tab_interview, tab_report = st.tabs(
    ["准备与出题", "虚拟面试官（F7）", "评分与复盘（F4/F6）"]
)


# ============================ Tab 1：双栏 Mockup 布局 ============================
with tab_prep:
    left, right = st.columns([1, 1.08], gap="large")

    # ---------- 左栏：F1 输入 + Tips ----------
    with left:
        # Resume card
        st.markdown(
            '<div class="ui-card">'
            '<div class="f-tag">F1</div>'
            '<div class="ui-card-title">Resume · 简历</div>'
            '<div class="ui-card-sub">Upload or paste your resume (CV) · 上传或粘贴简历</div>',
            unsafe_allow_html=True,
        )
        resume_file = st.file_uploader(
            "上传简历 PDF/TXT",
            type=["pdf", "txt"],
            key="resume_up",
            label_visibility="collapsed",
        )
        if resume_file is not None:
            raw_bytes = resume_file.getvalue()
            t = extract_text_from_upload(resume_file)
            if t:
                st.session_state.resume_text = t
            st.session_state.resume_filename = resume_file.name
            st.session_state.resume_filesize = len(raw_bytes)

        if st.session_state.resume_filename:
            st.markdown(
                styles.file_chip_html(
                    st.session_state.resume_filename,
                    format_size(st.session_state.resume_filesize)
                    if st.session_state.resume_filesize
                    else "已载入",
                ),
                unsafe_allow_html=True,
            )
            if st.button("清除已上传简历", key="btn_clear_resume", type="secondary"):
                st.session_state.resume_filename = ""
                st.session_state.resume_filesize = 0
                st.rerun()

        st.session_state.resume_text = st.text_area(
            "简历文本",
            value=st.session_state.resume_text,
            height=120,
            placeholder="或在此粘贴简历文本…",
            label_visibility="collapsed",
            key="resume_ta",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # JD card
        st.markdown(
            '<div class="ui-card">'
            '<div class="f-tag">F1</div>'
            '<div class="ui-card-title">Job Description · 岗位 JD</div>'
            '<div class="ui-card-sub">Paste the job description · 粘贴岗位描述</div>',
            unsafe_allow_html=True,
        )
        jd_file = st.file_uploader(
            "上传 JD",
            type=["pdf", "txt"],
            key="jd_up",
            label_visibility="collapsed",
        )
        if jd_file is not None:
            t = extract_text_from_upload(jd_file)
            if t:
                st.session_state.jd_text = t

        st.session_state.jd_text = st.text_area(
            "JD 文本",
            value=st.session_state.jd_text,
            height=140,
            placeholder="Paste JD here… / 在此粘贴 JD",
            label_visibility="collapsed",
            key="jd_ta",
            max_chars=5000,
        )
        jd_len = len(st.session_state.jd_text or "")
        st.markdown(
            f'<div class="char-counter">{jd_len} / 5000</div></div>',
            unsafe_allow_html=True,
        )

        # ---- F5 内置知识（主区左栏可见，不依赖侧边栏）----
        st.markdown(
            '<div class="ui-card">'
            '<div class="f-tag">F5 · 内置知识</div>'
            '<div class="ui-card-title">制药知识库 · GMP / CMC / 验证</div>'
            '<div class="ui-card-sub">'
            "Built-in knowledge for matching, questions & interview · "
            "出题、评分、追问共用；可预览并补充上传"
            "</div>",
            unsafe_allow_html=True,
        )
        with st.expander("预览内置知识（GMP / CMC / 验证要点）", expanded=False):
            st.text(knowledge.get_knowledge_preview(1200))
            st.download_button(
                "下载完整内置知识 (TXT)",
                data=knowledge.BUILTIN_KNOWLEDGE,
                file_name="pharma_builtin_knowledge.txt",
                mime="text/plain",
                key="dl_builtin_kb",
            )
        extra_file = st.file_uploader(
            "补充知识上传（可选，PDF/TXT）",
            type=["pdf", "txt"],
            key="extra_kb_main",
        )
        if extra_file is not None:
            extracted = extract_text_from_upload(extra_file)
            if extracted:
                st.session_state.extra_knowledge = extracted
                st.success(f"已载入补充知识（{len(extracted)} 字）")
        st.session_state.extra_knowledge = st.text_area(
            "补充知识文本（可选）",
            value=st.session_state.extra_knowledge,
            height=90,
            placeholder="可粘贴额外 SOP / 讲义摘要…",
            key="extra_kb_ta",
        )
        kb_chars = len(knowledge.BUILTIN_KNOWLEDGE) + len(
            st.session_state.extra_knowledge or ""
        )
        st.caption(f"当前知识上下文约 {kb_chars} 字（内置 + 补充）")
        st.markdown("</div>", unsafe_allow_html=True)

        # Tips
        st.markdown(styles.tips_card_html(), unsafe_allow_html=True)

        # Match trigger (F2) — 放在左栏底部，流程自然
        if st.button("分析匹配度 · Analyze Match（F2）", key="btn_match"):
            key = require_key()
            if key:
                if not st.session_state.resume_text.strip() and not st.session_state.jd_text.strip():
                    st.warning("请至少填写简历或 JD。")
                else:
                    with st.spinner("正在分析匹配度…"):
                        try:
                            msgs = llm.build_match_messages(
                                st.session_state.resume_text,
                                st.session_state.jd_text,
                                merged_knowledge(),
                            )
                            st.session_state.match_result = llm.chat_once(
                                msgs,
                                api_key=key,
                                base_url=st.session_state.base_url,
                                model=st.session_state.model,
                            )
                        except Exception as e:
                            st.error(str(e))

    # ---------- 右栏：F2 匹配分 + F3 题目 ----------
    with right:
        # Match Score card
        st.markdown(
            '<div class="ui-card">'
            '<div class="f-tag">F2 · Match Score</div>',
            unsafe_allow_html=True,
        )
        score = parse_match_score(st.session_state.match_result)
        status = parse_match_status(st.session_state.match_result, score)
        summary = parse_match_summary(st.session_state.match_result)
        gaps = parse_gaps(st.session_state.match_result)
        st.markdown(
            styles.match_score_html(score, status, summary, gaps),
            unsafe_allow_html=True,
        )

        n_q = st.slider("题目数量", 3, 8, 5, key="n_questions", label_visibility="collapsed")
        st.caption(f"将生成 {n_q} 道面试题")

        if st.button("✨ Generate Questions · 生成面试题（F3）", key="btn_questions"):
            key = require_key()
            if key:
                with st.spinner("正在出题…"):
                    try:
                        msgs = llm.build_question_messages(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            merged_knowledge(),
                            n=n_q,
                        )
                        st.session_state.questions_result = llm.chat_once(
                            msgs,
                            api_key=key,
                            base_url=st.session_state.base_url,
                            model=st.session_state.model,
                            temperature=0.55,
                        )
                    except Exception as e:
                        st.error(str(e))

        if st.session_state.match_result:
            with st.expander("查看完整匹配分析", expanded=False):
                st.markdown(st.session_state.match_result)
        st.markdown("</div>", unsafe_allow_html=True)

        # Questions card
        st.markdown(
            '<div class="ui-card">'
            '<div class="f-tag">F3</div>'
            '<div class="ui-card-title">Generated Interview Questions</div>'
            '<div class="ui-card-sub">Tailored to your background and the role. · 基于背景与岗位定制</div>',
            unsafe_allow_html=True,
        )
        q_list = parse_questions(st.session_state.questions_result)
        st.markdown(styles.questions_list_html(q_list), unsafe_allow_html=True)

        if st.session_state.questions_result and not q_list:
            # 解析失败时回退原文
            with st.expander("题目原文", expanded=True):
                st.markdown(st.session_state.questions_result)
        elif st.session_state.questions_result:
            with st.expander("题目详情（含考察点）", expanded=False):
                st.markdown(st.session_state.questions_result)

        # 选中题目带到 F7 / F4
        if q_list:
            pick = st.selectbox(
                "选中题目用于评分或虚拟面试",
                options=q_list,
                key="picked_q",
            )
            if pick:
                st.session_state.focus_question = pick

        if st.button("⚖ Score Answer · 评分作答（F4）", key="btn_toggle_score", type="secondary"):
            st.session_state.show_score_panel = not st.session_state.show_score_panel

        st.markdown("</div>", unsafe_allow_html=True)

        # F4 score panel（展开式，保持 mockup 次按钮语义）
        if st.session_state.show_score_panel:
            st.markdown(
                '<div class="ui-card">'
                '<div class="f-tag">F4 · Score Answer</div>'
                '<div class="ui-card-title">模拟作答与即时评分</div>'
                '<div class="ui-card-sub">针对某一题作答，模型按知识要点给出分数与缺漏</div>',
                unsafe_allow_html=True,
            )
            practice_q = st.text_area(
                "题目",
                value=st.session_state.focus_question,
                height=70,
                key="practice_q",
            )
            st.session_state.practice_answer = st.text_area(
                "你的作答",
                value=st.session_state.practice_answer,
                height=110,
                placeholder="写下你的回答…",
                key="practice_a",
            )
            if st.button("提交评分", key="btn_score"):
                key = require_key()
                if key:
                    if not practice_q.strip() or not st.session_state.practice_answer.strip():
                        st.warning("请填写题目与作答。")
                    else:
                        with st.spinner("评分中…"):
                            try:
                                msgs = llm.build_score_messages(
                                    practice_q,
                                    st.session_state.practice_answer,
                                    merged_knowledge(),
                                )
                                result = llm.chat_once(
                                    msgs,
                                    api_key=key,
                                    base_url=st.session_state.base_url,
                                    model=st.session_state.model,
                                )
                                st.session_state.practice_score = result
                                st.session_state.score_results = list(
                                    st.session_state.score_results
                                ) + [result]
                            except Exception as e:
                                st.error(str(e))
            if st.session_state.practice_score:
                st.markdown(st.session_state.practice_score)
            st.markdown("</div>", unsafe_allow_html=True)


# ============================ Tab 2：F7 ============================
with tab_interview:
    st.markdown(
        '<div class="ui-card">'
        '<div class="f-tag">F7 · 虚拟面试官（重点）</div>'
        '<div class="ui-card-title">多轮追问面试</div>'
        '<div class="ui-card-sub">建议围绕单题深入 3–5 轮；流式输出；可随时结束并生成总评</div>',
        unsafe_allow_html=True,
    )

    st.session_state.focus_question = st.text_area(
        "本轮焦点题目（可选，来自 F3）",
        value=st.session_state.focus_question,
        height=70,
        placeholder="留空则由面试官根据 JD/简历自主开场…",
    )

    b1, b2, b3 = st.columns(3)
    with b1:
        start_clicked = st.button("开始 / 重启面试", key="btn_start_iv")
    with b2:
        end_clicked = st.button("结束面试并生成总评", key="btn_end_iv", type="secondary")
    with b3:
        clear_clicked = st.button("清空对话", key="btn_clear_iv", type="secondary")

    if clear_clicked:
        st.session_state.interview_messages = []
        st.session_state.interview_started = False
        st.session_state.final_eval = ""
        st.rerun()

    if start_clicked:
        key = require_key()
        if key:
            st.session_state.interview_messages = []
            st.session_state.final_eval = ""
            st.session_state.interview_started = True
            system = llm.build_interviewer_system(
                st.session_state.resume_text,
                st.session_state.jd_text,
                merged_knowledge(),
                st.session_state.focus_question,
            )
            open_msgs = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": "请开始面试，先做简短寒暄（一两句），然后提出第一个问题。",
                },
            ]
            try:
                with st.spinner("面试官正在开场…"):
                    placeholder = st.empty()
                    acc = ""
                    for piece in llm.chat_stream(
                        open_msgs,
                        api_key=key,
                        base_url=st.session_state.base_url,
                        model=st.session_state.model,
                    ):
                        acc += piece
                        placeholder.markdown(
                            f'<div class="chat-label">面试官</div>'
                            f'<div class="chat-assistant">{acc}</div>',
                            unsafe_allow_html=True,
                        )
                    st.session_state.interview_messages.append(
                        {"role": "assistant", "content": acc}
                    )
                    st.rerun()
            except Exception as e:
                st.session_state.interview_started = False
                st.error(str(e))

    for m in st.session_state.interview_messages:
        if m["role"] == "assistant":
            st.markdown(
                f'<div class="chat-label">面试官</div>'
                f'<div class="chat-assistant">{m["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-label" style="text-align:right">你</div>'
                f'<div class="chat-user">{m["content"]}</div>',
                unsafe_allow_html=True,
            )

    if st.session_state.interview_started and not st.session_state.final_eval:
        user_reply = st.chat_input("输入你的回答，回车发送…")
        if user_reply:
            key = require_key()
            if key:
                st.session_state.interview_messages.append(
                    {"role": "user", "content": user_reply}
                )
                system = llm.build_interviewer_system(
                    st.session_state.resume_text,
                    st.session_state.jd_text,
                    merged_knowledge(),
                    st.session_state.focus_question,
                )
                api_messages = [{"role": "system", "content": system}] + list(
                    st.session_state.interview_messages
                )
                try:
                    placeholder = st.empty()
                    acc = ""
                    for piece in llm.chat_stream(
                        api_messages,
                        api_key=key,
                        base_url=st.session_state.base_url,
                        model=st.session_state.model,
                    ):
                        acc += piece
                        placeholder.markdown(
                            f'<div class="chat-label">面试官</div>'
                            f'<div class="chat-assistant">{acc}</div>',
                            unsafe_allow_html=True,
                        )
                    st.session_state.interview_messages.append(
                        {"role": "assistant", "content": acc}
                    )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    if end_clicked:
        key = require_key()
        if key:
            if not st.session_state.interview_messages:
                st.warning("暂无面试对话，请先开始面试。")
            else:
                with st.spinner("正在生成综合总评…"):
                    try:
                        msgs = llm.build_final_eval_messages(
                            st.session_state.interview_messages,
                            merged_knowledge(),
                        )
                        st.session_state.final_eval = llm.chat_once(
                            msgs,
                            api_key=key,
                            base_url=st.session_state.base_url,
                            model=st.session_state.model,
                            temperature=0.35,
                        )
                        st.session_state.interview_started = False
                    except Exception as e:
                        st.error(str(e))

    if st.session_state.final_eval:
        st.markdown("---")
        st.markdown("##### 综合总评（F4 / F6）")
        st.markdown(st.session_state.final_eval)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================ Tab 3：F6 ============================
with tab_report:
    st.markdown(
        '<div class="ui-card">'
        '<div class="f-tag">F6 · 结果展示与复盘</div>'
        '<div class="ui-card-title">面试复盘报告</div>'
        '<div class="ui-card-sub">汇总匹配分析、题目、单题评分与虚拟面试总评</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cols[0].metric("匹配分析", f"{parse_match_score(st.session_state.match_result) or '—'}%")
    cols[1].metric("面试题", f"{len(parse_questions(st.session_state.questions_result))} 道")
    cols[2].metric("单题评分", f"{len(st.session_state.score_results)} 条")
    cols[3].metric("面试总评", "已有" if st.session_state.final_eval else "—")

    if st.button("一键生成复盘报告", key="btn_report"):
        key = require_key()
        if key:
            with st.spinner("汇总生成报告中…"):
                try:
                    msgs = llm.build_report_messages(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        st.session_state.match_result,
                        st.session_state.questions_result,
                        st.session_state.score_results,
                        st.session_state.final_eval,
                    )
                    st.session_state.report_result = llm.chat_once(
                        msgs,
                        api_key=key,
                        base_url=st.session_state.base_url,
                        model=st.session_state.model,
                        temperature=0.4,
                    )
                except Exception as e:
                    st.error(str(e))

    if st.session_state.report_result:
        st.markdown(st.session_state.report_result)
        st.download_button(
            "下载复盘报告 (Markdown)",
            data=st.session_state.report_result,
            file_name="interview_review_report.md",
            mime="text/markdown",
        )
    else:
        st.markdown(
            '<p class="pharma-hint">建议先完成匹配 / 出题 / 虚拟面试，再生成完整复盘。</p>',
            unsafe_allow_html=True,
        )

    with st.expander("回看 · F2 匹配结果", expanded=False):
        st.markdown(st.session_state.match_result or "_暂无_")
    with st.expander("回看 · F3 面试题", expanded=False):
        st.markdown(st.session_state.questions_result or "_暂无_")
    with st.expander("回看 · F4 单题评分", expanded=False):
        if st.session_state.score_results:
            for i, s in enumerate(st.session_state.score_results, 1):
                st.markdown(f"**评分记录 {i}**")
                st.markdown(s)
                st.markdown("---")
        else:
            st.markdown("_暂无_")
    with st.expander("回看 · F7 面试总评", expanded=False):
        st.markdown(st.session_state.final_eval or "_暂无_")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        '<p class="pharma-hint">单用户本地课程演示：无登录、无数据库；刷新后会话清空。</p>',
        unsafe_allow_html=True,
    )
