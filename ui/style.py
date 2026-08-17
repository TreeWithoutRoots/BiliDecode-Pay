"""Y2K 像素风格 CSS 注入 — CRT 终端美学"""

import streamlit as st
import streamlit.components.v1 as components

from config import Y2K_COLORS, GOOGLE_FONTS_URL


def inject_y2k_style():
    """注入 Y2K 像素风格全局 CSS"""

    st.markdown(
        f'<link href="{GOOGLE_FONTS_URL}" rel="stylesheet">',
        unsafe_allow_html=True,
    )

    css = f"""
    <style>
    /* ═══════════════════════════════════════════
       全局基础
       ═══════════════════════════════════════════ */
    html, body, [class*="css"] {{
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        -webkit-font-smoothing: none !important;
        font-smooth: never !important;
    }}
    ::selection {{
        background: {Y2K_COLORS["accent_secondary"]} !important;
        color: {Y2K_COLORS["bg_main"]} !important;
    }}

    /* ═══════════════════════════════════════════
       主背景 — 深空 + 网格 + 星点
       ═══════════════════════════════════════════ */
    .stApp {{
        background-color: {Y2K_COLORS["bg_main"]} !important;
        background-image:
            linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px),
            radial-gradient(circle at 15% 25%, rgba(255, 42, 109, 0.08) 0%, transparent 35%),
            radial-gradient(circle at 85% 70%, rgba(0, 240, 255, 0.06) 0%, transparent 35%),
            radial-gradient(circle at 50% 50%, rgba(255, 215, 0, 0.03) 0%, transparent 50%);
        background-size: 24px 24px, 24px 24px, 100% 100%, 100% 100%, 100% 100%;
        background-attachment: fixed;
    }}

    /* CRT 扫描线覆盖层 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            rgba(0, 0, 0, 0.06) 0px,
            rgba(0, 0, 0, 0.06) 1px,
            transparent 1px,
            transparent 3px
        );
        pointer-events: none;
        z-index: 9999;
    }}
    /* CRT 暗角 */
    .stApp::after {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.4) 100%);
        pointer-events: none;
        z-index: 9998;
    }}

    /* ═══════════════════════════════════════════
       标题层级
       ═══════════════════════════════════════════ */
    h1, h2, h3 {{
        font-family: 'Press Start 2P', cursive !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        letter-spacing: 1px;
        text-shadow: 2px 2px 0 rgba(255, 42, 109, 0.5);
    }}
    h4, h5, h6 {{
        font-family: 'Silkscreen', monospace !important;
        color: {Y2K_COLORS["accent_secondary"]} !important;
        letter-spacing: 0.5px;
    }}

    /* ═══════════════════════════════════════════
       页面头部 — 故障风标题
       ═══════════════════════════════════════════ */
    .y2k-header {{
        text-align: center;
        padding: 28px 0 20px;
        position: relative;
    }}
    .y2k-header::before {{
        content: "";
        display: block;
        height: 4px;
        background: repeating-linear-gradient(
            90deg,
            {Y2K_COLORS["accent_primary"]} 0, {Y2K_COLORS["accent_primary"]} 8px,
            transparent 8px, transparent 16px,
            {Y2K_COLORS["accent_secondary"]} 16px, {Y2K_COLORS["accent_secondary"]} 24px,
            transparent 24px, transparent 32px
        );
        margin-bottom: 20px;
    }}
    .y2k-header h1 {{
        font-family: 'Press Start 2P', cursive;
        font-size: 32px;
        color: {Y2K_COLORS["accent_primary"]};
        text-shadow:
            3px 0 0 {Y2K_COLORS["accent_secondary"]},
            -3px 0 0 {Y2K_COLORS["accent_primary"]},
            0 0 20px rgba(0, 240, 255, 0.3);
        margin: 0;
        animation: glitch 4s infinite;
    }}
    .y2k-header p {{
        font-family: 'VT323', monospace;
        font-size: 20px;
        color: {Y2K_COLORS["text_dim"]};
        margin: 12px 0 0;
        letter-spacing: 2px;
    }}
    .y2k-header p::after {{
        content: "_";
        animation: blink 1s step-end infinite;
        color: {Y2K_COLORS["accent_secondary"]};
    }}
    @keyframes glitch {{
        0%, 92%, 100% {{ transform: none; opacity: 1; }}
        93% {{ transform: translateX(-2px); text-shadow: 3px 0 0 {Y2K_COLORS["accent_secondary"]}, -3px 0 0 {Y2K_COLORS["accent_primary"]}; }}
        94% {{ transform: translateX(2px); text-shadow: -3px 0 0 {Y2K_COLORS["accent_secondary"]}, 3px 0 0 {Y2K_COLORS["accent_primary"]}; }}
        95% {{ transform: none; }}
    }}
    @keyframes blink {{
        50% {{ opacity: 0; }}
    }}

    /* ═══════════════════════════════════════════
       输入框
       ═══════════════════════════════════════════ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-left: 4px solid {Y2K_COLORS["accent_primary"]} !important;
        border-radius: 0 !important;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.1) !important;
        background: {Y2K_COLORS["bg_card"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 20px !important;
        color: {Y2K_COLORS["text_main"]} !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {Y2K_COLORS["accent_primary"]} !important;
        border-left-color: {Y2K_COLORS["accent_secondary"]} !important;
        box-shadow: 0 0 16px rgba(0, 240, 255, 0.25) !important;
    }}
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: {Y2K_COLORS["text_dim"]} !important;
    }}

    /* ═══════════════════════════════════════════
       按钮 — 像素按下效果
       ═══════════════════════════════════════════ */
    .stButton > button {{
        border: 2px solid {Y2K_COLORS["accent_primary"]} !important;
        border-radius: 0 !important;
        box-shadow:
            4px 4px 0 {Y2K_COLORS["accent_secondary"]},
            0 0 15px rgba(0, 240, 255, 0.2) !important;
        background: {Y2K_COLORS["bg_card"]} !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        font-family: 'Press Start 2P', cursive !important;
        font-size: 12px !important;
        padding: 14px 24px !important;
        transition: all 0.1s ease !important;
        cursor: pointer;
        position: relative;
    }}
    .stButton > button:hover {{
        background: {Y2K_COLORS["accent_primary"]} !important;
        color: {Y2K_COLORS["bg_main"]} !important;
        border-color: {Y2K_COLORS["accent_secondary"]} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0 {Y2K_COLORS["accent_secondary"]}, 0 0 20px rgba(0, 240, 255, 0.3) !important;
    }}
    .stButton > button:active {{
        transform: translate(4px, 4px) !important;
        box-shadow: 0 0 0 {Y2K_COLORS["accent_secondary"]} !important;
    }}

    /* 下载按钮 — 不同配色 */
    .stDownloadButton > button {{
        border-color: {Y2K_COLORS["accent_secondary"]} !important;
        box-shadow: 4px 4px 0 {Y2K_COLORS["accent_primary"]}, 0 0 15px rgba(255, 42, 109, 0.15) !important;
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    .stDownloadButton > button:hover {{
        background: {Y2K_COLORS["accent_secondary"]} !important;
        color: {Y2K_COLORS["bg_main"]} !important;
        border-color: {Y2K_COLORS["accent_primary"]} !important;
        box-shadow: 2px 2px 0 {Y2K_COLORS["accent_primary"]}, 0 0 20px rgba(255, 42, 109, 0.3) !important;
    }}

    /* ═══════════════════════════════════════════
       下拉框
       ═══════════════════════════════════════════ */
    .stSelectbox label {{
        font-family: 'VT323', monospace !important;
        font-size: 20px !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
    }}
    .stSelectbox > div > div {{
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-left: 4px solid {Y2K_COLORS["accent_secondary"]} !important;
        border-radius: 0 !important;
        background: {Y2K_COLORS["bg_card"]} !important;
    }}

    /* ═══════════════════════════════════════════
       Tab 导航 — Y2K 文件夹标签
       ═══════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px;
        background: transparent;
        border-bottom: 3px solid {Y2K_COLORS["border"]} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Press Start 2P', cursive !important;
        font-size: 11px !important;
        color: {Y2K_COLORS["text_dim"]} !important;
        background: {Y2K_COLORS["bg_card"]} !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-bottom: none !important;
        border-radius: 0 !important;
        padding: 10px 20px !important;
        margin-right: 2px !important;
        transition: all 0.15s ease !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
        background: rgba(255, 42, 109, 0.1) !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {Y2K_COLORS["accent_primary"]} !important;
        background: {Y2K_COLORS["bg_main"]} !important;
        border-color: {Y2K_COLORS["accent_primary"]} !important;
        border-bottom: 3px solid {Y2K_COLORS["bg_main"]} !important;
        margin-bottom: -3px !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.4) !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {Y2K_COLORS["accent_primary"]} !important;
        height: 0 !important;
    }}
    .stTabs [data-baseweb="tab-border-bottom"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 20px !important;
    }}

    /* ═══════════════════════════════════════════
       折叠面板
       ═══════════════════════════════════════════ */
    .streamlit-expanderHeader {{
        font-family: 'Press Start 2P', cursive !important;
        font-size: 11px !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        background: {Y2K_COLORS["bg_card"]} !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-left: 4px solid {Y2K_COLORS["accent_primary"]} !important;
    }}
    .streamlit-expanderHeader:hover {{
        border-left-color: {Y2K_COLORS["accent_secondary"]} !important;
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    .streamlit-expanderContent {{
        background: {Y2K_COLORS["bg_card_light"]} !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-top: none !important;
    }}

    /* ─── 折叠面板内：浅底深字 ─── */
    .streamlit-expanderContent .stMarkdown p,
    .streamlit-expanderContent .stMarkdown li,
    .streamlit-expanderContent .stMarkdown ul,
    .streamlit-expanderContent .stMarkdown ol,
    .streamlit-expanderContent .stMarkdown em,
    .streamlit-expanderContent .stMarkdown blockquote {{
        color: #1a1a2e !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
    }}
    .streamlit-expanderContent .stMarkdown strong {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    .streamlit-expanderContent .stMarkdown code {{
        color: {Y2K_COLORS["error"]} !important;
        background: rgba(255, 0, 64, 0.08) !important;
        padding: 2px 6px !important;
        border-radius: 0 !important;
    }}
    .streamlit-expanderContent h1,
    .streamlit-expanderContent h2,
    .streamlit-expanderContent h3 {{
        color: #1a1a2e !important;
        text-shadow: none !important;
    }}
    .streamlit-expanderContent table {{
        width: 100% !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-collapse: collapse !important;
    }}
    .streamlit-expanderContent th {{
        background: {Y2K_COLORS["accent_primary"]} !important;
        color: {Y2K_COLORS["bg_main"]} !important;
        font-family: 'VT323', monospace !important;
        border: 1px solid {Y2K_COLORS["border"]} !important;
        padding: 8px !important;
    }}
    .streamlit-expanderContent td {{
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border: 1px solid {Y2K_COLORS["border"]} !important;
        padding: 6px 8px !important;
        color: #1a1a2e !important;
    }}

    /* ═══════════════════════════════════════════
       Markdown 正文 — 深底亮字
       ═══════════════════════════════════════════ */
    .stMarkdown p, .stMarkdown li, .stMarkdown ul,
    .stMarkdown ol, .stMarkdown em, .stMarkdown blockquote {{
        color: {Y2K_COLORS["text_main"]} !important;
        font-size: 18px !important;
        line-height: 1.7 !important;
    }}
    .stMarkdown strong {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
        color: {Y2K_COLORS["accent_primary"]} !important;
    }}
    .stMarkdown table {{
        width: 100% !important;
        border: 2px solid {Y2K_COLORS["accent_primary"]} !important;
        border-collapse: collapse !important;
        margin: 12px 0 !important;
    }}
    .stMarkdown th {{
        background: rgba(0, 240, 255, 0.15) !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border: 1px solid rgba(0, 240, 255, 0.4) !important;
        padding: 8px !important;
    }}
    .stMarkdown td {{
        color: {Y2K_COLORS["text_main"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border: 1px solid rgba(0, 240, 255, 0.25) !important;
        padding: 6px 8px !important;
    }}
    .stMarkdown code {{
        color: {Y2K_COLORS["success"]} !important;
        background: rgba(57, 255, 20, 0.1) !important;
        padding: 2px 6px !important;
        border-radius: 0 !important;
    }}
    .stMarkdown blockquote {{
        border-left: 4px solid {Y2K_COLORS["accent_secondary"]} !important;
        background: rgba(255, 42, 109, 0.05) !important;
        padding: 8px 16px !important;
        margin: 8px 0 !important;
    }}

    /* ═══════════════════════════════════════════
       侧边栏
       ═══════════════════════════════════════════ */
    section[data-testid="stSidebar"] {{
        background-color: {Y2K_COLORS["bg_main"]} !important;
        border-right: 3px solid {Y2K_COLORS["accent_primary"]} !important;
        box-shadow: inset -2px 0 20px rgba(0, 240, 255, 0.05) !important;
    }}
    section[data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: repeating-linear-gradient(
            90deg,
            {Y2K_COLORS["accent_primary"]} 0, {Y2K_COLORS["accent_primary"]} 6px,
            {Y2K_COLORS["accent_secondary"]} 6px, {Y2K_COLORS["accent_secondary"]} 12px
        );
    }}
    section[data-testid="stSidebar"] label {{
        color: {Y2K_COLORS["accent_primary"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 20px !important;
    }}

    .y2k-sidebar-title {{
        font-family: 'Press Start 2P', cursive !important;
        font-size: 14px !important;
        color: {Y2K_COLORS["accent_secondary"]} !important;
        text-shadow: 2px 2px 0 rgba(0, 240, 255, 0.3);
        text-align: center;
        padding: 16px 0 !important;
        border-bottom: 2px dashed {Y2K_COLORS["border"]} !important;
        margin-bottom: 16px;
    }}

    /* ═══════════════════════════════════════════
       状态指示器
       ═══════════════════════════════════════════ */
    .y2k-status {{
        font-family: 'Press Start 2P', cursive;
        font-size: 10px;
        padding: 10px 16px;
        border: 2px solid;
        display: inline-block;
        margin: 6px 0;
    }}
    .y2k-status-info {{
        background: {Y2K_COLORS["bg_card"]};
        color: {Y2K_COLORS["accent_primary"]};
        border-color: {Y2K_COLORS["accent_primary"]};
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.15);
    }}
    .y2k-status-success {{
        background: rgba(57, 255, 20, 0.15);
        color: {Y2K_COLORS["success"]};
        border-color: {Y2K_COLORS["success"]};
        box-shadow: 0 0 12px rgba(57, 255, 20, 0.15);
    }}
    .y2k-status-error {{
        background: rgba(255, 0, 64, 0.15);
        color: {Y2K_COLORS["error"]};
        border-color: {Y2K_COLORS["error"]};
        box-shadow: 0 0 12px rgba(255, 0, 64, 0.15);
    }}

    /* ═══════════════════════════════════════════
       进度条 — 像素段
       ═══════════════════════════════════════════ */
    .stProgress > div > div {{
        background: {Y2K_COLORS["bg_card"]} !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-radius: 0 !important;
        height: 20px !important;
    }}
    .stProgress > div > div > div {{
        background: repeating-linear-gradient(
            90deg,
            {Y2K_COLORS["accent_primary"]} 0, {Y2K_COLORS["accent_primary"]} 6px,
            {Y2K_COLORS["accent_secondary"]} 6px, {Y2K_COLORS["accent_secondary"]} 12px
        ) !important;
        border-radius: 0 !important;
    }}

    /* ═══════════════════════════════════════════
       链接
       ═══════════════════════════════════════════ */
    a {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
        text-decoration: underline !important;
        text-underline-offset: 3px;
    }}
    a:hover {{
        color: {Y2K_COLORS["accent_primary"]} !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
    }}

    /* ═══════════════════════════════════════════
       水平线 — 像素虚线
       ═══════════════════════════════════════════ */
    hr {{
        border: none !important;
        height: 2px !important;
        background: repeating-linear-gradient(
            90deg,
            {Y2K_COLORS["border"]} 0, {Y2K_COLORS["border"]} 4px,
            transparent 4px, transparent 8px
        ) !important;
        margin: 20px 0 !important;
    }}

    /* ═══════════════════════════════════════════
       滚动条
       ═══════════════════════════════════════════ */
    ::-webkit-scrollbar {{
        width: 12px;
    }}
    ::-webkit-scrollbar-track {{
        background: {Y2K_COLORS["bg_main"]};
        border-left: 2px solid {Y2K_COLORS["border"]};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {Y2K_COLORS["accent_primary"]};
        border: 2px solid {Y2K_COLORS["bg_main"]};
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {Y2K_COLORS["accent_secondary"]};
    }}

    /* ═══════════════════════════════════════════
       Streamlit 默认元素隐藏
       ═══════════════════════════════════════════ */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* ═══════════════════════════════════════════
       入场动画
       ═══════════════════════════════════════════ */
    @keyframes fade-in-up {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .stTabs, .y2k-header {{
        animation: fade-in-up 0.5s ease-out;
    }}
    .stMarkdown, .stButton, .stTextInput, .stSelectbox {{
        animation: fade-in-up 0.4s ease-out;
    }}

    /* ═══════════════════════════════════════════
       Material 图标颜色覆盖
       ═══════════════════════════════════════════ */
    span[data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
        -webkit-text-fill-color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    components.html(
        """
        <script>
        function fixIconColors() {
            try {
                var doc = window.parent.document;
                var icons = doc.querySelectorAll('[data-testid="stIconMaterial"]');
                icons.forEach(function(el) {
                    el.style.setProperty('color', '#FF2A6D', 'important');
                    el.style.setProperty('-webkit-text-fill-color', '#FF2A6D', 'important');
                    el.removeAttribute('color');
                });
            } catch(e) {}
        }
        setInterval(fixIconColors, 500);
        </script>
        """,
        height=0,
    )


def render_header():
    """渲染 Y2K 风格页面头部"""
    st.markdown(
        """
        <div class="y2k-header">
            <h1>BILIDECODE</h1>
            <p>B站视频分析终端 v1.0</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
