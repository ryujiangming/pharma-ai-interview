# 制药行业 AI 面试助手

课程作业 Streamlit 应用：极简高级 UI，基于 OpenAI 兼容 API（默认 DeepSeek），覆盖 URS 功能 **F1–F7**。

## 功能对照（URS）

| 编号 | 功能 | 说明 |
|------|------|------|
| F1 | 资料输入 | 粘贴或上传简历 / JD（PDF、TXT） |
| F2 | 匹配分析 | 简历 × JD，结合制药知识输出匹配度与缺口 |
| F3 | 生成面试题 | 一键生成 5–8 道个性化面试题（技术/情景/GMP/CMC） |
| F4 | 回答评分 | 单题 1–10 分 + 评语；虚拟面试结束后综合评分 |
| F5 | 内置知识 | GMP / CMC / 验证要点；可补充上传 |
| F6 | 结果展示 | 卡片与复盘报告清晰汇总 |
| F7 | 虚拟面试官 | **重点**：多轮追问、流式输出，建议每题 3–5 轮 |

**推荐操作路径：** 输入简历+JD → 匹配结果(F2) → 生成面试题(F3) → 虚拟面试官(F7) → 结束并评价/复盘(F4/F6)

## 快速运行

```bash
cd /workspace/pharma-ai-interview
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

浏览器打开终端提示的地址（默认本项目配置为 `http://localhost:8502`）。

## API Key 配置

任选其一：

1. **侧边栏「API 配置」** 直接填写 API Key（推荐课程演示）
2. **环境变量**（勿把真实 Key 写进代码仓库）：
   ```bash
   export DEEPSEEK_API_KEY="sk-..."
   # 或
   export OPENAI_API_KEY="sk-..."
   ```

默认：

- `base_url` = `https://api.deepseek.com`
- `model` = `deepseek-chat`

可在侧边栏改成任意 OpenAI 兼容服务。

## 项目结构

```
pharma-ai-interview/
├── app.py                 # 主界面与 F1–F7 流程
├── knowledge.py           # F5 内置 GMP/CMC/验证知识
├── llm.py                 # OpenAI 兼容调用与 Prompt
├── styles.py              # 极简高级 CSS
├── requirements.txt
├── README.md
└── .streamlit/config.toml # 浅色中性主题
```

## 说明与限制

- 单用户本地演示：无登录、无数据库；刷新后会话清空。
- 真正调用大模型需要有效 API Key 与网络。
- 可选 TTS（语音播报）未实现，仅预留扩展空间。
- 代码含中文注释，便于学生阅读与修改。
