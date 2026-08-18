"""BiliDecode —— B站视频分析终端（公开元数据分析版）"""

import re
import os
import sys

import streamlit as st
from dotenv import load_dotenv

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# ─── Streamlit Cloud Secrets 兼容 ───
# 本地用 .env，云端用 st.secrets，这里统一加载到环境变量
for _key in ("DASHSCOPE_API_KEY", "SUPABASE_URL", "SUPABASE_SECRET_KEY",
             "WAFFO_MERCHANT_ID", "WAFFO_STORE_SLUG", "WAFFO_PRIVATE_KEY",
             "WAFFO_PRODUCT_ID", "WAFFO_SUCCESS_URL", "WAFFO_ENVIRONMENT",
             "WAFFO_CURRENCY"):
    if _key not in os.environ:
        try:
            os.environ[_key] = st.secrets[_key]
        except (KeyError, FileNotFoundError):
            pass

from config import BAILIAN_MODELS, DEFAULT_MODEL, Y2K_COLORS
from utils.url_parser import parse_url
from core.bilibili_client import fetch_video_data
from core.analyzer import analyze_video_metadata
from core.supabase_client import (
    is_configured as sb_configured,
    save_analysis as sb_save,
    get_history as sb_history,
    get_history_count as sb_count,
    get_report_by_id as sb_report,
    get_stats as sb_stats,
)
from core.waffo_client import WaffoClient
from ui.style import inject_y2k_style, render_header
from ui.components import (
    pixel_status, pixel_progress, render_cost_box, render_cover_preview,
    render_video_dashboard, generate_report_md, generate_dashboard_md,
)


# ─── 页面配置 ───
st.set_page_config(
    page_title="BiliDecode - B站视频分析终端",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_y2k_style()
render_header()

# ─── Waffo 支付初始化 ───
waffo = WaffoClient()

# 检测支付回调（用户从 Waffo 结账页面返回）
if "session_id" in st.query_params:
    _session_id = st.query_params.get("session_id", "")
    _paid_bvid = st.query_params.get("bvid", "")
    _paid_model = st.query_params.get("model", DEFAULT_MODEL)

    _verified = waffo.verify_payment(_session_id)

    if _verified:
        st.session_state["paid_bvid"] = _paid_bvid
        st.session_state["paid_model"] = _paid_model
        st.session_state["auto_analyze"] = True
    else:
        st.session_state["payment_error"] = "支付验证失败，请重新支付"
    st.query_params.clear()
    st.rerun()


# ─── 侧边栏：系统状态 ───
with st.sidebar:
    st.markdown(
        '<div class="y2k-sidebar-title">⚙ SYSTEM</div>',
        unsafe_allow_html=True,
    )

    # Supabase 连接状态
    sb_ok = sb_configured()
    sb_icon = "✅" if sb_ok else "❌"
    sb_text = "Supabase 已连接" if sb_ok else "Supabase 未配置"
    st.markdown(
        f"<div style='font-family: VT323, monospace; font-size: 18px; "
        f"color: {Y2K_COLORS['accent_primary']};'>"
        f"{sb_icon} {sb_text}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Waffo 支付状态
    waffo_ok = waffo.is_configured()
    waffo_icon = "✅" if waffo_ok else "⬜"
    waffo_text = "Waffo 支付已启用" if waffo_ok else "Waffo 支付未配置"
    st.markdown(
        f"<div style='font-family: VT323, monospace; font-size: 18px; "
        f"color: {Y2K_COLORS['accent_primary']};'>"
        f"{waffo_icon} {waffo_text}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        f"<div style='font-family: VT323, monospace; font-size: 18px; "
        f"color: {Y2K_COLORS['accent_primary']}; "
        f"border-left: 3px solid {Y2K_COLORS['accent_secondary']}; "
        f"padding-left: 12px;'>"
        "本项目仅采集B站公开元数据<br>"
        "不下载视频内容"
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
#  Tab 导航
# ═══════════════════════════════════════════
tab_analyze, tab_history, tab_dashboard = st.tabs(
    ["🔍 分析", "📜 历史记录", "📊 仪表盘"]
)


# ═══════════════════════════════════════════
#  Tab 1: 分析
# ═══════════════════════════════════════════
with tab_analyze:
    _pay_err = st.session_state.pop("payment_error", None)
    if _pay_err:
        pixel_status(f"ERROR: {_pay_err}", "error")

    st.markdown("### INPUT VIDEO URL")

    col1, col2 = st.columns([3, 1])

    with col1:
        url_input = st.text_input(
            "B站视频链接",
            placeholder="https://www.bilibili.com/video/BVxxxxxxxx",
            label_visibility="collapsed",
            key="url_input",
        )

    with col2:
        model_options = {key: info["label"] for key, info in BAILIAN_MODELS.items()}
        selected_model_label = st.selectbox(
            "模型",
            options=list(model_options.values()),
            index=0,
            label_visibility="collapsed",
        )
        selected_model = next(
            key for key, label in model_options.items() if label == selected_model_label
        )

    _btn_label = "PAY & ANALYZE" if waffo.is_configured() else "START ANALYSIS"
    analyze_btn = st.button(_btn_label, use_container_width=True)


    # ─── 报告拆分 ───
    def split_report_sections(report_text: str) -> list[tuple[str, str]]:
        pattern = r"(^|\n)(#{1,2}\s+[^#\n]+)"
        parts = re.split(pattern, report_text)

        sections = []
        current_title = ""
        current_content = ""

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            if re.match(r"^#{1,2}\s+", part):
                if current_title:
                    sections.append((current_title, current_content.strip()))
                current_title = re.sub(r"^#{1,2}\s+", "", part)
                current_content = ""
            else:
                current_content += part + "\n"

        if current_title:
            sections.append((current_title, current_content.strip()))

        return sections


    # ─── 分析逻辑 ───
    should_analyze = False

    # 支付回调：自动开始分析
    if st.session_state.pop("auto_analyze", False):
        bvid = st.session_state.pop("paid_bvid", "")
        selected_model = st.session_state.pop("paid_model", DEFAULT_MODEL)
        should_analyze = True

    if analyze_btn:
        if not os.getenv("DASHSCOPE_API_KEY"):
            pixel_status("ERROR: 服务端未配置 API Key，请联系管理员", "error")
            st.stop()

        if not url_input.strip():
            pixel_status("ERROR: 请输入B站视频链接", "error")
            st.stop()

        bvid = parse_url(url_input)
        if not bvid:
            pixel_status("ERROR: 无法解析BV号，请检查链接是否正确", "error")
            st.stop()

        # Waffo 支付流程：创建结账会话并跳转
        if waffo.is_configured():
            import streamlit.components.v1 as components
            _success_url = (
                f"{waffo.success_url}"
                f"?session_id={{SESSION_ID}}&bvid={bvid}&model={selected_model}"
            )
            with st.spinner("正在创建支付订单..."):
                _session = waffo.create_checkout_session(success_url=_success_url)
            if _session and _session.get("checkoutUrl"):
                _checkout_url = _session["checkoutUrl"]
                st.markdown(
                    f"<div style='text-align:center; padding:20px;'>"
                    f"<p style='font-family: Press Start 2P, cursive; font-size: 12px; "
                    f"color: {Y2K_COLORS['accent_primary']}; letter-spacing: 1px; "
                    f"margin-bottom: 16px;'>PAYMENT READY</p>"
                    f"<p style='font-family: VT323, monospace; font-size: 20px; "
                    f"color: {Y2K_COLORS['text_main']};'>"
                    f"支付订单已创建，请点击下方按钮完成支付</p></div>",
                    unsafe_allow_html=True,
                )
                st.link_button(
                    "💳 前往支付页面",
                    _checkout_url,
                    use_container_width=True,
                )
                st.stop()
            else:
                pixel_status("ERROR: 创建支付订单失败，请稍后重试", "error")
                st.stop()

        should_analyze = True

    if should_analyze or st.session_state.get("last_result"):
        if should_analyze:
            pixel_status(f"BVID: {bvid}  MODEL: {selected_model}", "info")

            with st.status("分析进行中...", expanded=True) as status:
                st.write("📡 采集视频元数据...")
                pixel_progress("FETCHING DATA", 15)

                video_data = fetch_video_data(bvid)

                if not video_data.title:
                    status.update(label="采集失败", state="error")
                    pixel_status(
                        f"ERROR: {video_data.errors[0] if video_data.errors else '视频数据采集失败'}",
                        "error",
                    )
                    st.stop()

                st.write(f"✅ 视频标题：{video_data.title}")
                pixel_progress("DATA FETCHED", 30)

                st.write("💬 采集热门评论与弹幕...")
                pixel_progress("FETCHING COMMENTS", 50)

                st.write(f"🤖 调用 {selected_model} 分析中...")
                pixel_progress("AI ANALYSIS", 70)

                result = analyze_video_metadata(video_data, model=selected_model)

                if result.error:
                    status.update(label="分析失败", state="error")
                    pixel_status(f"ERROR: {result.error}", "error")
                    st.stop()

                pixel_progress("ANALYSIS COMPLETE", 100)
                status.update(label="分析完成!", state="complete")

            st.session_state["last_video_data"] = video_data
            st.session_state["last_result"] = result
            st.session_state["last_url"] = url_input.strip()

            if sb_configured():
                saved = sb_save(video_data, result, video_url=url_input.strip())
                st.session_state["last_save_status"] = "saved" if saved else "failed"
        else:
            video_data = st.session_state["last_video_data"]
            result = st.session_state["last_result"]

        # ─── 展示结果 ───
        st.markdown("---")

        if video_data.cover_url:
            st.markdown("#### COVER PREVIEW")
            render_cover_preview(video_data.cover_url, video_data.title)

        if video_data.errors:
            with st.expander("⚠ 数据采集异常记录", expanded=False):
                for err in video_data.errors:
                    st.markdown(f"- {err}")

        st.markdown("### 📋 ANALYSIS REPORT")

        sections = split_report_sections(result.text)

        if sections:
            for title, content in sections:
                with st.expander(title, expanded=(title == sections[0][0])):
                    st.markdown(content)
        else:
            st.markdown(result.text)

        st.markdown("---")
        render_cost_box(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost=result.estimated_cost,
            model=result.model,
        )

        # ─── 单视频数据看板 ───
        st.markdown("### 📊 VIDEO DASHBOARD")
        render_video_dashboard(video_data=video_data, result=result)

        # ─── 下载按钮 ───
        st.markdown("### 📥 DOWNLOAD")
        report_md = generate_report_md(video_data=video_data, result=result)
        dashboard_md = generate_dashboard_md(video_data=video_data)

        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="📄 下载分析报告 (.md)",
                data=report_md.encode("utf-8"),
                file_name=f"report_{video_data.bvid}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl_col2:
            st.download_button(
                label="📊 下载数据看板 (.md)",
                data=dashboard_md.encode("utf-8"),
                file_name=f"dashboard_{video_data.bvid}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ─── Supabase 保存状态 ───
        _save_status = st.session_state.get("last_save_status")
        if _save_status == "saved":
            st.markdown(
                f"<div style='font-family: VT323, monospace; font-size: 18px; "
                f"color: {Y2K_COLORS['success']}; "
                f"border-left: 3px solid {Y2K_COLORS['success']}; "
                f"padding-left: 12px; margin-top: 8px;'>"
                f"✅ 分析记录已保存到 Supabase"
                f"</div>",
                unsafe_allow_html=True,
            )
        elif _save_status == "failed":
            st.markdown(
                f"<div style='font-family: VT323, monospace; font-size: 18px; "
                f"color: {Y2K_COLORS['error']}; "
                f"border-left: 3px solid {Y2K_COLORS['error']}; "
                f"padding-left: 12px; margin-top: 8px;'>"
                f"⚠ Supabase 保存失败，不影响本次分析结果"
                f"</div>",
                unsafe_allow_html=True,
            )

    elif not should_analyze:
        _btn_label = 'PAY & ANALYZE' if waffo.is_configured() else 'START ANALYSIS'
        _pay_note = f"<span style='color: {Y2K_COLORS['accent_secondary']};'>💳 本次分析需要通过 Waffo 支付后进行。</span><br>" if waffo.is_configured() else ""
        st.markdown(
            f"""
            <div style="font-family: VT323, monospace; font-size: 19px; color: {Y2K_COLORS['accent_primary']}; border: 2px solid {Y2K_COLORS['border']}; border-left: 4px solid {Y2K_COLORS['accent_primary']}; background: {Y2K_COLORS['bg_card']}; padding: 20px 24px; margin-top: 12px; line-height: 1.8;">
            <span style="font-family: Press Start 2P, cursive; font-size: 11px; color: {Y2K_COLORS['accent_secondary']}; display: block; margin-bottom: 12px; letter-spacing: 1px;">READY</span>
            📺 在上方输入B站视频链接，选择模型后点击 {_btn_label} 开始分析。<br>
            系统将采集视频公开元数据（标题、统计、评论、弹幕、封面等），<br>
            调用阿里百炼多模态大模型生成六维度结构化分析报告。<br>
            {_pay_note}<br>
            <span style="color: {Y2K_COLORS['accent_primary']};">支持的链接格式：</span><br>
            <span style="color: {Y2K_COLORS['accent_secondary']};">• https://www.bilibili.com/video/BVxxxxxxxx</span><br>
            <span style="color: {Y2K_COLORS['accent_secondary']};">• https://b23.tv/xxxxxxx</span><br>
            <span style="color: {Y2K_COLORS['accent_secondary']};">• https://m.bilibili.com/video/BVxxxxxxxx</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════
#  Tab 2: 历史记录
# ═══════════════════════════════════════════
with tab_history:
    if "viewing_report" not in st.session_state:
        st.session_state["viewing_report"] = None

    if not sb_configured():
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 20px; "
            f"color: {Y2K_COLORS['accent_secondary']}; "
            f"border: 2px solid {Y2K_COLORS['accent_secondary']}; "
            f"border-left: 4px solid {Y2K_COLORS['accent_secondary']}; "
            f"padding: 20px; text-align: center; "
            f"background: {Y2K_COLORS['bg_card']};'>"
            "⚠ Supabase 未配置<br>"
            "请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_SECRET_KEY"
            f"</div>",
            unsafe_allow_html=True,
        )
    elif st.session_state["viewing_report"]:
        # ─── 报告详情页 ───
        report_id = st.session_state["viewing_report"]
        full_record = sb_report(report_id)

        if st.button("⬅ 返回列表", key="back_btn"):
            st.session_state["viewing_report"] = None
            st.rerun()

        if full_record:
            title = full_record.get("title", "未知标题")
            bvid = full_record.get("bvid", "")
            up = full_record.get("up_name", "")
            st.markdown(
                f"<div style='font-family: Press Start 2P, cursive; font-size: 14px; "
                f"color: {Y2K_COLORS['accent_secondary']}; margin: 15px 0;'>"
                f"{title}"
                f"</div>",
                unsafe_allow_html=True,
            )

            # 视频数据看板
            st.markdown("### 📊 VIDEO DASHBOARD")
            render_video_dashboard(record=full_record)

            # 分析报告
            st.markdown("### 📋 ANALYSIS REPORT")
            report_text = full_record.get("report_text", "")
            if report_text:
                sections = split_report_sections(report_text)
                if sections:
                    for s_title, s_content in sections:
                        with st.expander(s_title, expanded=(s_title == sections[0][0])):
                            st.markdown(s_content)
                else:
                    st.markdown(report_text)
            else:
                st.warning("报告内容为空")

            # 下载按钮
            st.markdown("### 📥 DOWNLOAD")
            report_md = generate_report_md(record=full_record)
            dashboard_md = generate_dashboard_md(record=full_record)
            safe_bvid = bvid or "unknown"

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    label="📄 下载分析报告 (.md)",
                    data=report_md.encode("utf-8"),
                    file_name=f"report_{safe_bvid}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with dl_col2:
                st.download_button(
                    label="📊 下载数据看板 (.md)",
                    data=dashboard_md.encode("utf-8"),
                    file_name=f"dashboard_{safe_bvid}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
        else:
            st.error("无法加载报告数据")
    else:
        # ─── 历史列表页 ───
        st.markdown("### 📜 ANALYSIS HISTORY")
        total = sb_count()
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 20px; "
            f"color: {Y2K_COLORS['accent_primary']}; margin-bottom: 15px;'>"
            f"共 {total} 条分析记录"
            f"</div>",
            unsafe_allow_html=True,
        )

        if total > 0:
            history = sb_history(limit=50)

            for record in history:
                with st.container():
                    st.markdown(
                        f"<div style='border: 2px solid {Y2K_COLORS['border']}; "
                        f"border-left: 4px solid {Y2K_COLORS['accent_primary']}; "
                        f"background: {Y2K_COLORS['bg_card']}; "
                        f"padding: 12px 16px; margin-bottom: 8px;'>",
                        unsafe_allow_html=True,
                    )
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        title = record.get("title", "未知标题")
                        bvid = record.get("bvid", "")
                        up = record.get("up_name", "")
                        st.markdown(
                            f"**{title}**<br>"
                            f"<span style='color: {Y2K_COLORS['accent_primary']}; "
                            f"font-family: VT323, monospace; font-size: 18px;'>"
                            f"BV号: {bvid} | UP主: {up}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    with col2:
                        model = record.get("model_used", "")
                        cost = record.get("estimated_cost", 0) or 0
                        st.markdown(
                            f"<span style='font-family: VT323, monospace; "
                            f"font-size: 18px; color: {Y2K_COLORS['accent_secondary']};'>"
                            f"模型: {model}<br>费用: ¥{cost:.4f}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    with col3:
                        created = record.get("created_at", "")
                        date_str = created[:16].replace("T", " ") if created else ""
                        view_count = record.get("view_count", 0) or 0
                        st.markdown(
                            f"<span style='font-family: VT323, monospace; "
                            f"font-size: 18px; color: {Y2K_COLORS['accent_primary']};'>"
                            f"播放: {view_count:,}<br>{date_str}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    report_id = record.get("id", "")
                    if st.button("查看报告", key=f"btn_{report_id}"):
                        st.session_state["viewing_report"] = report_id
                        st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.markdown(
                f"<div style='font-family: VT323, monospace; font-size: 20px; "
                f"color: {Y2K_COLORS['accent_primary']}; text-align: center; "
                f"padding: 40px; "
                f"border: 2px dashed {Y2K_COLORS['border']}; "
                f"background: {Y2K_COLORS['bg_card']};'>"
                "暂无分析记录，去「分析」Tab 开始第一次分析吧！"
                f"</div>",
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════
#  Tab 3: 仪表盘
# ═══════════════════════════════════════════
with tab_dashboard:
    st.markdown("### 📊 DASHBOARD")

    if not sb_configured():
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 20px; "
            f"color: {Y2K_COLORS['accent_secondary']}; "
            f"border: 2px solid {Y2K_COLORS['accent_secondary']}; "
            f"border-left: 4px solid {Y2K_COLORS['accent_secondary']}; "
            f"padding: 20px; text-align: center; "
            f"background: {Y2K_COLORS['bg_card']};'>"
            "⚠ Supabase 未配置<br>"
            "请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_SECRET_KEY"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        stats = sb_stats()

        if stats.get("total", 0) == 0:
            st.markdown(
                f"<div style='font-family: VT323, monospace; font-size: 20px; "
                f"color: {Y2K_COLORS['accent_primary']}; text-align: center; "
                f"padding: 40px; "
                f"border: 2px dashed {Y2K_COLORS['border']}; "
                f"background: {Y2K_COLORS['bg_card']};'>"
                "暂无数据，去「分析」Tab 生成第一份报告吧！"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            # ─── 核心指标卡片 ───
            col1, col2, col3, col4 = st.columns(4)

            def metric_card(label: str, value: str, color: str):
                st.markdown(
                    f"<div style='border: 2px solid {color}; "
                    f"border-left: 4px solid {color}; "
                    f"box-shadow: 0 0 14px rgba(0,0,0,0.3); "
                    f"padding: 16px 12px; "
                    f"background: {Y2K_COLORS['bg_card']}; text-align: center; "
                    f"margin-bottom: 10px;'>"
                    f"<div style='font-family: Press Start 2P, cursive; "
                    f"font-size: 9px; color: {color}; letter-spacing: 1px;'>{label}</div>"
                    f"<div style='font-family: VT323, monospace; "
                    f"font-size: 28px; color: {Y2K_COLORS['text_main']}; "
                    f"margin-top: 8px; "
                    f"text-shadow: 0 0 6px rgba(0,0,0,0.3);'>{value}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col1:
                metric_card("总分析次数", str(stats["total"]), Y2K_COLORS["accent_primary"])
            with col2:
                total_views = stats.get("total_views", 0)
                metric_card("总播放量", f"{total_views:,}", Y2K_COLORS["accent_secondary"])
            with col3:
                avg_eng = stats.get("avg_engagement_rate", 0)
                metric_card("平均互动率", f"{avg_eng}%", Y2K_COLORS["success"])
            with col4:
                up_count = len(stats.get("up_distribution", {}))
                metric_card("覆盖UP主", str(up_count), Y2K_COLORS["error"])

            st.markdown("---")

            # ─── Plotly 图表 ───
            try:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots

                PINK = Y2K_COLORS["accent_secondary"]
                CYAN = Y2K_COLORS["accent_primary"]
                GREEN = Y2K_COLORS["success"]
                RED = Y2K_COLORS["error"]
                BG = Y2K_COLORS["bg_main"]

                plotly_layout = dict(
                    paper_bgcolor=BG,
                    plot_bgcolor=BG,
                    font=dict(family="VT323, monospace", size=16, color=Y2K_COLORS["text_main"]),
                    margin=dict(l=40, r=20, t=50, b=40),
                )

                col_left, col_right = st.columns(2)

                # ─── 左列：近7天分析趋势 ───
                with col_left:
                    st.markdown("#### 近7天分析趋势")
                    recent = stats.get("recent_7d", [])
                    if recent:
                        dates = [r["date"][5:] for r in recent]
                        counts = [r["count"] for r in recent]

                        fig = go.Figure(data=go.Scatter(
                            x=dates,
                            y=counts,
                            mode="lines+markers",
                            line=dict(color=CYAN, width=3),
                            marker=dict(size=10, color=PINK, line=dict(width=2, color="#000")),
                            fill="tozeroy",
                            fillcolor="rgba(0, 240, 255, 0.08)",
                        ))
                        fig.update_layout(**plotly_layout, height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    # ─── Top5 互动数据对比 ───
                    st.markdown("#### Top 5 视频互动数据")
                    top_eng = stats.get("top_engagement", [])
                    if top_eng:
                        short_titles = [
                            t["title"][:12] + "…" if len(t["title"]) > 12 else t["title"]
                            for t in top_eng
                        ]
                        fig2 = go.Figure(data=[
                            go.Bar(name="点赞", x=short_titles,
                                   y=[t["likes"] for t in top_eng],
                                   marker_color=PINK),
                            go.Bar(name="投币", x=short_titles,
                                   y=[t["coins"] for t in top_eng],
                                   marker_color=CYAN),
                            go.Bar(name="收藏", x=short_titles,
                                   y=[t["favorites"] for t in top_eng],
                                   marker_color=GREEN),
                        ])
                        fig2.update_layout(
                            **plotly_layout,
                            barmode="group",
                            height=300,
                            showlegend=True,
                            legend=dict(font=dict(color=Y2K_COLORS["text_main"])),
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                # ─── 右列：Top5 播放量 + UP主分布 ───
                with col_right:
                    st.markdown("#### Top 5 播放量视频")
                    top_viewed = stats.get("top_viewed", [])
                    if top_viewed:
                        titles = [t["title"][:15] + "…" if len(t["title"]) > 15 else t["title"]
                                  for t in top_viewed]
                        views = [t["view_count"] for t in top_viewed]

                        fig3 = go.Figure(data=go.Bar(
                            x=views,
                            y=titles,
                            orientation="h",
                            marker_color=PINK,
                            marker_line=dict(width=2, color="#000"),
                            text=[f"{v:,}" for v in views],
                            textposition="outside",
                            textfont=dict(color=CYAN, size=14),
                        ))
                        fig3.update_layout(
                            **plotly_layout,
                            height=350,
                            yaxis=dict(autorange="reversed"),
                            xaxis=dict(color=CYAN),
                        )
                        st.plotly_chart(fig3, use_container_width=True)

                    # ─── UP主分析覆盖 ───
                    st.markdown("#### UP主分析覆盖")
                    up_dist = stats.get("up_distribution", {})
                    if up_dist:
                        sorted_ups = sorted(up_dist.items(), key=lambda x: x[1], reverse=True)[:8]
                        up_names = [u[0][:10] + "…" if len(u[0]) > 10 else u[0] for u in sorted_ups]
                        up_counts = [u[1] for u in sorted_ups]

                        fig4 = go.Figure(data=go.Bar(
                            x=up_names,
                            y=up_counts,
                            marker_color=CYAN,
                            marker_line=dict(width=2, color="#000"),
                            text=[f"{c}" for c in up_counts],
                            textposition="outside",
                            textfont=dict(color=PINK, size=16),
                        ))
                        fig4.update_layout(
                            **plotly_layout,
                            height=300,
                            xaxis=dict(color=CYAN),
                            yaxis=dict(color=Y2K_COLORS["text_main"]),
                        )
                        st.plotly_chart(fig4, use_container_width=True)

            except ImportError:
                st.warning("图表功能需要 plotly 库，请运行: pip install plotly")
