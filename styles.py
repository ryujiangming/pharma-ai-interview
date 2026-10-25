# -*- coding: utf-8 -*-
"""
UI 样式 — 贴近 mockup：白/浅灰底、钢蓝强调色、双栏卡片、大留白、轻阴影。
"""

# 钢蓝强调色（与 mockup 一致）
ACCENT = "#3B7EA6"
ACCENT_HOVER = "#336F94"
ACCENT_SOFT = "rgba(59, 126, 166, 0.12)"
ACCENT_MUTED = "#6B9BB8"
BG = "#F5F6F8"
TEXT = "#1C1C1E"
MUTED = "#8E8E93"
BORDER = "rgba(0,0,0,0.07)"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
  font-family: Inter, -apple-system, BlinkMacSystemFont, "PingFang SC",
               "Noto Sans SC", "Microsoft YaHei", sans-serif;
}}

.stApp {{
  background: {BG};
  color: {TEXT};
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

.block-container {{
  padding-top: 1.25rem !important;
  padding-bottom: 3.5rem !important;
  max-width: 1120px !important;
}}

/* ---------- Header ---------- */
.app-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding: 0.25rem 0 0.75rem 0;
}}
.app-header-left {{
  display: flex;
  align-items: center;
  gap: 0.7rem;
}}
.app-logo {{
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: {ACCENT};
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  box-shadow: 0 4px 12px {ACCENT_SOFT};
}}
.app-title-wrap h1 {{
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  color: {TEXT};
  line-height: 1.25;
}}
.app-title-wrap .sub {{
  font-size: 0.78rem;
  color: {MUTED};
  margin: 0.1rem 0 0 0;
}}
.app-header-right {{
  display: flex;
  align-items: center;
  gap: 0.85rem;
}}
.how-link {{
  color: {MUTED};
  font-size: 0.86rem;
  font-weight: 500;
  text-decoration: none;
}}
.avatar {{
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #E8EEF2;
  color: {ACCENT};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
}}

/* ---------- Cards ---------- */
.ui-card {{
  background: #FFFFFF;
  border: 1px solid {BORDER};
  border-radius: 14px;
  padding: 1.15rem 1.25rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03), 0 6px 20px rgba(0,0,0,0.035);
  margin-bottom: 0.9rem;
}}
.ui-card-title {{
  font-size: 1.02rem;
  font-weight: 650;
  color: {TEXT};
  margin: 0 0 0.2rem 0;
}}
.ui-card-sub {{
  font-size: 0.8rem;
  color: {MUTED};
  margin: 0 0 0.85rem 0;
  line-height: 1.45;
}}
.f-tag {{
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 600;
  color: {ACCENT};
  background: {ACCENT_SOFT};
  padding: 0.12rem 0.45rem;
  border-radius: 6px;
  margin-bottom: 0.45rem;
  letter-spacing: 0.02em;
}}

/* ---------- Dropzone / file chip ---------- */
.dropzone {{
  border: 1.5px dashed #C9D4DC;
  border-radius: 12px;
  background: #FAFBFC;
  padding: 0.85rem 1rem;
  min-height: 64px;
  display: flex;
  align-items: center;
}}
.file-chip {{
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  background: #EEF3F7;
  border-radius: 10px;
  padding: 0.45rem 0.7rem;
  max-width: 100%;
}}
.file-chip .pdf-ico {{
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: #E2554A;
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.file-chip .meta {{
  display: flex;
  flex-direction: column;
  min-width: 0;
}}
.file-chip .name {{
  font-size: 0.82rem;
  font-weight: 600;
  color: {TEXT};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.file-chip .size {{
  font-size: 0.7rem;
  color: {MUTED};
}}
.drop-hint {{
  color: {MUTED};
  font-size: 0.82rem;
}}

/* ---------- Tips row ---------- */
.tips-row {{
  display: flex;
  gap: 0.75rem;
  justify-content: space-between;
}}
.tip-item {{
  flex: 1;
  text-align: center;
  padding: 0.35rem 0.25rem;
}}
.tip-ico {{
  width: 36px;
  height: 36px;
  margin: 0 auto 0.45rem auto;
  border-radius: 50%;
  background: {ACCENT_SOFT};
  color: {ACCENT};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}}
.tip-item p {{
  margin: 0;
  font-size: 0.72rem;
  color: #5C6670;
  line-height: 1.35;
}}

/* ---------- Match score ---------- */
.match-top {{
  display: flex;
  align-items: flex-start;
  gap: 1.1rem;
  margin-bottom: 0.85rem;
}}
.match-pct {{
  font-size: 3.1rem;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: {TEXT};
  line-height: 1;
  min-width: 4.2rem;
}}
.match-meta {{
  flex: 1;
  padding-top: 0.25rem;
}}
.match-status {{
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 650;
  font-size: 0.95rem;
  color: {TEXT};
  margin-bottom: 0.25rem;
}}
.match-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: {ACCENT};
  display: inline-block;
}}
.match-summary {{
  font-size: 0.82rem;
  color: {MUTED};
  line-height: 1.45;
  margin: 0;
}}
.gap-list {{
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 1rem 0;
}}
.gap-list li {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.45rem 0;
  border-top: 1px solid rgba(0,0,0,0.045);
  font-size: 0.84rem;
  color: #3A3A3C;
}}
.gap-list li:first-child {{ border-top: none; }}
.gap-tag {{
  flex-shrink: 0;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.18rem 0.5rem;
  border-radius: 999px;
}}
.gap-tag.medium {{
  background: {ACCENT_SOFT};
  color: {ACCENT};
}}
.gap-tag.low {{
  background: #EEF0F2;
  color: #6E7781;
}}
.gap-tag.high {{
  background: rgba(226, 85, 74, 0.12);
  color: #C44;
}}

/* ---------- Question rows ---------- */
.q-list {{
  list-style: none;
  padding: 0;
  margin: 0.35rem 0 0.9rem 0;
}}
.q-list li {{
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.15rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}}
.q-list li:last-child {{ border-bottom: none; }}
.q-num {{
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: {ACCENT};
  color: #fff;
  font-size: 0.75rem;
  font-weight: 650;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.q-text {{
  flex: 1;
  font-size: 0.88rem;
  color: {TEXT};
  line-height: 1.4;
}}
.q-chevron {{
  color: #B0B8C0;
  font-size: 1.1rem;
  flex-shrink: 0;
}}

/* ---------- Empty states ---------- */
.empty-hint {{
  color: {MUTED};
  font-size: 0.84rem;
  line-height: 1.5;
  padding: 0.5rem 0 0.25rem 0;
}}
.char-counter {{
  text-align: right;
  font-size: 0.72rem;
  color: {MUTED};
  margin-top: -0.35rem;
  margin-bottom: 0.2rem;
}}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
  background: #FFFFFF;
  border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: 1.25rem !important;
}}

/* ---------- Buttons ---------- */
.stButton > button {{
  border-radius: 11px !important;
  border: none !important;
  background: {ACCENT} !important;
  color: #fff !important;
  font-weight: 600 !important;
  padding: 0.55rem 1.15rem !important;
  box-shadow: 0 4px 14px {ACCENT_SOFT} !important;
  transition: background 0.15s ease, transform 0.15s ease !important;
  width: 100%;
}}
.stButton > button:hover {{
  background: {ACCENT_HOVER} !important;
  transform: translateY(-1px) !important;
}}
/* secondary / outlined */
div[data-testid="stButton"] > button[kind="secondary"],
.stButton > button[kind="secondary"] {{
  background: #FFFFFF !important;
  color: {ACCENT} !important;
  border: 1.5px solid {ACCENT} !important;
  box-shadow: none !important;
}}
.stButton > button[kind="secondary"]:hover {{
  background: {ACCENT_SOFT} !important;
}}

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea {{
  border-radius: 10px !important;
  border-color: rgba(0,0,0,0.08) !important;
  background: #FAFBFC !important;
}}
.stTextArea textarea {{
  min-height: 110px;
}}

/* file uploader soften */
[data-testid="stFileUploader"] section {{
  border: 1.5px dashed #C9D4DC !important;
  border-radius: 12px !important;
  background: #FAFBFC !important;
  padding: 0.5rem !important;
}}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{
  gap: 0.35rem;
  background: transparent;
  border-bottom: 1px solid {BORDER};
  margin-bottom: 0.85rem;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: 10px 10px 0 0;
  padding: 0.5rem 1rem;
  color: {MUTED};
  font-weight: 500;
}}
.stTabs [aria-selected="true"] {{
  color: {ACCENT} !important;
  background: {ACCENT_SOFT} !important;
}}

/* ---------- Chat (F7) ---------- */
.chat-user {{
  background: {ACCENT_SOFT};
  border-radius: 14px 14px 4px 14px;
  padding: 0.85rem 1rem;
  margin: 0.4rem 0 0.4rem 18%;
  color: {TEXT};
  line-height: 1.55;
}}
.chat-assistant {{
  background: #FFFFFF;
  border: 1px solid {BORDER};
  border-radius: 14px 14px 14px 4px;
  padding: 0.85rem 1rem;
  margin: 0.4rem 18% 0.4rem 0;
  color: {TEXT};
  line-height: 1.55;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}}
.chat-label {{
  font-size: 0.72rem;
  color: {MUTED};
  margin-bottom: 0.2rem;
  font-weight: 500;
}}

.pharma-hint {{
  color: {MUTED};
  font-size: 0.84rem;
  line-height: 1.5;
}}

/* metric polish */
[data-testid="stMetric"] {{
  background: #FAFBFC;
  border: 1px solid {BORDER};
  border-radius: 12px;
  padding: 0.65rem 0.8rem;
}}
</style>
"""


def inject_styles():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    """顶部栏：医疗十字图标 + 双语标题 + How it works。"""
    import streamlit as st
    st.markdown(
        """
<div class="app-header">
  <div class="app-header-left">
    <div class="app-logo">+</div>
    <div class="app-title-wrap">
      <h1>Pharma Interview Assistant</h1>
      <p class="sub">制药行业 AI 面试助手 · 课程作业</p>
    </div>
  </div>
  <div class="app-header-right">
    <span class="how-link">ⓘ How it works</span>
    <div class="avatar">A</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def tips_card_html() -> str:
    return """
<div class="ui-card">
  <div class="ui-card-title" style="font-size:0.92rem;margin-bottom:0.75rem;">
    What this helps you with
  </div>
  <div class="tips-row">
    <div class="tip-item">
      <div class="tip-ico">◎</div>
      <p>Predict relevant<br/>questions<br/><span style="color:#3B7EA6;font-size:0.65rem;">预测相关问题</span></p>
    </div>
    <div class="tip-item">
      <div class="tip-ico">▤</div>
      <p>Assess your<br/>readiness<br/><span style="color:#3B7EA6;font-size:0.65rem;">评估准备度</span></p>
    </div>
    <div class="tip-item">
      <div class="tip-ico">✓</div>
      <p>Improve with<br/>feedback<br/><span style="color:#3B7EA6;font-size:0.65rem;">反馈改进</span></p>
    </div>
  </div>
</div>
"""


def file_chip_html(name: str, size_label: str) -> str:
    safe = name.replace("<", "").replace(">", "")
    ext = "PDF" if safe.lower().endswith(".pdf") else "TXT"
    return f"""
<div class="dropzone">
  <div class="file-chip">
    <div class="pdf-ico">{ext}</div>
    <div class="meta">
      <span class="name">{safe}</span>
      <span class="size">{size_label}</span>
    </div>
  </div>
</div>
"""


def match_score_html(
    score: int | None,
    status: str,
    summary: str,
    gaps: list[tuple[str, str]],
) -> str:
    """gaps: list of (text, level) where level in high/medium/low."""
    pct = f"{score}%" if score is not None else "—"
    if not gaps:
        gaps_html = (
            '<p class="empty-hint">完成匹配分析后，缺口要点将显示在这里。</p>'
        )
    else:
        items = []
        for text, level in gaps:
            tag_label = {
                "high": "High gap",
                "medium": "Medium gap",
                "low": "Low gap",
            }.get(level, "Gap")
            items.append(
                f'<li><span>{text}</span>'
                f'<span class="gap-tag {level}">{tag_label}</span></li>'
            )
        gaps_html = '<ul class="gap-list">' + "".join(items) + "</ul>"

    return f"""
<div class="match-top">
  <div class="match-pct">{pct}</div>
  <div class="match-meta">
    <div class="match-status"><span class="match-dot"></span> {status}</div>
    <p class="match-summary">{summary}</p>
  </div>
</div>
{gaps_html}
"""


def questions_list_html(questions: list[str]) -> str:
    if not questions:
        return '<p class="empty-hint">生成面试题后，题目将以列表形式展示于此。</p>'
    items = []
    for i, q in enumerate(questions, 1):
        safe = (
            q.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        items.append(
            f'<li><div class="q-num">{i}</div>'
            f'<div class="q-text">{safe}</div>'
            f'<div class="q-chevron">›</div></li>'
        )
    return '<ul class="q-list">' + "".join(items) + "</ul>"
