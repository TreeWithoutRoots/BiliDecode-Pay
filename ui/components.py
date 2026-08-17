"""Y2K 像素风自定义 Streamlit 组件"""

import base64
import streamlit as st
import requests

from config import Y2K_COLORS


def render_video_dashboard(video_data=None, result=None, record=None):
    """
    渲染单视频数据看板。
    可传入 VideoData 对象，或传入 Supabase 记录字典 (record)。
    """
    if record:
        title = record.get("title", "未知标题")
        bvid = record.get("bvid", "")
        up_name = record.get("up_name", "")
        views = record.get("view_count", 0) or 0
        likes = record.get("like_count", 0) or 0
        coins = record.get("coin_count", 0) or 0
        favorites = record.get("favorite_count", 0) or 0
        cover_url = record.get("cover_url", "")
        report_text = record.get("report_text", "")
        model = record.get("model_used", "")
        created = record.get("created_at", "")
        desc = ""
        duration = 0
        pubdate = ""
        tags = []
        shares = 0
        replies = 0
        danmaku = 0
    else:
        title = video_data.title
        bvid = video_data.bvid
        up_name = video_data.owner_name
        views = video_data.stat_view
        likes = video_data.stat_like
        coins = video_data.stat_coin
        favorites = video_data.stat_favorite
        cover_url = video_data.cover_url
        report_text = result.text if result else ""
        model = result.model if result else ""
        desc = video_data.desc
        duration = video_data.duration
        pubdate = video_data.pubdate
        tags = video_data.tags
        shares = video_data.stat_share
        replies = video_data.stat_reply
        danmaku = video_data.stat_danmaku

    engagement = 0.0
    if views > 0:
        engagement = round((likes + coins + favorites) / views * 100, 2)

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    def stat_card(label, value, color):
        st.markdown(
            f"<div class='y2k-stat-card' style='"
            f"border: 2px solid {color}; "
            f"border-left: 4px solid {color}; "
            f"box-shadow: 0 0 12px rgba({_hex_to_rgb(color)}, 0.1); "
            f"padding: 12px 8px; "
            f"background: {Y2K_COLORS['bg_card']}; "
            f"text-align: center; "
            f"margin-bottom: 8px; "
            f"transition: all 0.15s ease;'>"
            f"<div style='font-family: Press Start 2P, cursive; font-size: 8px; "
            f"color: {color}; letter-spacing: 1px;'>{label}</div>"
            f"<div style='font-family: VT323, monospace; font-size: 24px; "
            f"color: {Y2K_COLORS['text_main']}; margin-top: 6px; "
            f"text-shadow: 0 0 6px rgba({_hex_to_rgb(color)}, 0.2);'>{value}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col1:
        stat_card("PLAYS", f"{views:,}", Y2K_COLORS["accent_primary"])
    with col2:
        stat_card("LIKES", f"{likes:,}", Y2K_COLORS["accent_secondary"])
    with col3:
        stat_card("COINS", f"{coins:,}", Y2K_COLORS["success"])
    with col4:
        stat_card("FAVS", f"{favorites:,}", Y2K_COLORS["error"])
    with col5:
        stat_card("ENG%", f"{engagement}%", Y2K_COLORS["accent_tertiary"])

    if desc:
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 18px; "
            f"color: {Y2K_COLORS['text_dim']}; margin: 12px 0 6px; "
            f"border-left: 3px solid {Y2K_COLORS['accent_secondary']}; "
            f"padding-left: 12px;'>"
            f"<strong style='color: {Y2K_COLORS['accent_secondary']};'>BRIEF:</strong> {desc}"
            f"</div>",
            unsafe_allow_html=True,
        )
    if tags:
        tag_html = " ".join(
            f"<span style='font-family: VT323, monospace; font-size: 16px; "
            f"color: {Y2K_COLORS['accent_primary']}; "
            f"border: 1px solid {Y2K_COLORS['border']}; "
            f"padding: 2px 8px; margin: 2px 4px 2px 0; "
            f"background: {Y2K_COLORS['bg_card']}; "
            f"display: inline-block;'>#{t}</span>"
            for t in tags
        )
        st.markdown(
            f"<div style='margin: 8px 0;'>{tag_html}</div>",
            unsafe_allow_html=True,
        )

    try:
        import plotly.graph_objects as go
        fig = go.Figure(data=go.Bar(
            x=["点赞", "投币", "收藏", "分享", "评论", "弹幕"],
            y=[likes, coins, favorites, shares, replies, danmaku],
            marker_color=[
                Y2K_COLORS["accent_secondary"],
                Y2K_COLORS["accent_primary"],
                Y2K_COLORS["success"],
                Y2K_COLORS["error"],
                Y2K_COLORS["accent_tertiary"],
                "#FF69B4",
            ],
            marker_line=dict(width=2, color="#000"),
            text=[f"{v:,}" for v in [likes, coins, favorites, shares, replies, danmaku]],
            textposition="outside",
            textfont=dict(color=Y2K_COLORS["accent_primary"], size=14),
        ))
        fig.update_layout(
            paper_bgcolor=Y2K_COLORS["bg_main"],
            plot_bgcolor=Y2K_COLORS["bg_main"],
            font=dict(family="VT323, monospace", size=16, color=Y2K_COLORS["text_main"]),
            margin=dict(l=30, r=20, t=20, b=30),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass

    st.markdown("---")


def generate_report_md(video_data=None, result=None, record=None):
    """生成分析报告的 Markdown 文本"""
    if record:
        title = record.get("title", "未知")
        bvid = record.get("bvid", "")
        up_name = record.get("up_name", "")
        views = record.get("view_count", 0) or 0
        likes = record.get("like_count", 0) or 0
        coins = record.get("coin_count", 0) or 0
        favorites = record.get("favorite_count", 0) or 0
        report_text = record.get("report_text", "")
        model = record.get("model_used", "")
        created = record.get("created_at", "")
    else:
        title = video_data.title
        bvid = video_data.bvid
        up_name = video_data.owner_name
        views = video_data.stat_view
        likes = video_data.stat_like
        coins = video_data.stat_coin
        favorites = video_data.stat_favorite
        report_text = result.text if result else ""
        model = result.model if result else ""

    engagement = round((likes + coins + favorites) / max(views, 1) * 100, 2)

    md = f"""# B站视频分析报告

## 视频信息

| 字段 | 内容 |
|------|------|
| 标题 | {title} |
| BV号 | {bvid} |
| UP主 | {up_name} |
| 模型 | {model} |
| 生成时间 | {created[:19].replace("T", " ") if record else ""} |

## 核心数据

| 指标 | 数值 |
|------|------|
| 播放量 | {views:,} |
| 点赞 | {likes:,} |
| 投币 | {coins:,} |
| 收藏 | {favorites:,} |
| 互动率 | {engagement}% |

---

## 分析报告正文

{report_text}
"""
    return md


def generate_dashboard_md(video_data=None, record=None):
    """生成视频数据看板的 Markdown 文本"""
    if record:
        title = record.get("title", "未知")
        bvid = record.get("bvid", "")
        up_name = record.get("up_name", "")
        views = record.get("view_count", 0) or 0
        likes = record.get("like_count", 0) or 0
        coins = record.get("coin_count", 0) or 0
        favorites = record.get("favorite_count", 0) or 0
    else:
        title = video_data.title
        bvid = video_data.bvid
        up_name = video_data.owner_name
        views = video_data.stat_view
        likes = video_data.stat_like
        coins = video_data.stat_coin
        favorites = video_data.stat_favorite
        shares = video_data.stat_share
        replies = video_data.stat_reply
        danmaku = video_data.stat_danmaku
        desc = video_data.desc
        tags = video_data.tags

    engagement = round((likes + coins + favorites) / max(views, 1) * 100, 2)

    md = f"""# 视频数据看板

## 基础信息

- **标题**: {title}
- **BV号**: {bvid}
- **UP主**: {up_name}

## 核心指标

| 指标 | 数值 | 占播放量比 |
|------|------|-----------|
| 播放量 | {views:,} | 100% |
| 点赞 | {likes:,} | {round(likes / max(views, 1) * 100, 2)}% |
| 投币 | {coins:,} | {round(coins / max(views, 1) * 100, 2)}% |
| 收藏 | {favorites:,} | {round(favorites / max(views, 1) * 100, 2)}% |
| **互动率** | **{likes + coins + favorites:,}** | **{engagement}%** |
"""

    if not record:
        md += f"""
## 互动数据

| 指标 | 数值 |
|------|------|
| 分享 | {shares:,} |
| 评论 | {replies:,} |
| 弹幕 | {danmaku:,} |
"""
        if desc:
            md += f"\n## 视频简介\n\n{desc}\n"
        if tags:
            md += f"\n## 标签\n\n{', '.join('#' + t for t in tags)}\n"

    return md


def pixel_status(text: str, level: str = "info"):
    """
    渲染像素风状态指示器。
    level: "info" | "success" | "error"
    """
    st.markdown(
        f'<div class="y2k-status y2k-status-{level}">{text}</div>',
        unsafe_allow_html=True,
    )


def pixel_progress(label: str, percent: int):
    """渲染像素风进度条。"""
    st.markdown(
        f"""
        <div style="font-family: 'Press Start 2P', cursive; font-size: 10px;
                    color: {Y2K_COLORS['accent_primary']}; margin-bottom: 6px;
                    letter-spacing: 1px;">
            {label} <span style="color: {Y2K_COLORS['text_dim']};">[{percent}%]</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(percent / 100)


def render_cost_box(input_tokens: int, output_tokens: int, cost: float, model: str):
    """渲染 Token 用量和费用信息"""
    st.markdown(
        f"""
        <div style="
            border: 2px solid {Y2K_COLORS['accent_primary']};
            border-left: 4px solid {Y2K_COLORS['accent_secondary']};
            box-shadow: 0 0 16px rgba(0, 240, 255, 0.1);
            background: {Y2K_COLORS['bg_card']};
            padding: 16px 20px;
            margin-top: 20px;
        ">
            <div style="font-family: 'Press Start 2P', cursive; font-size: 10px;
                        color: {Y2K_COLORS['accent_secondary']};
                        letter-spacing: 1px; margin-bottom: 12px;">
                ANALYSIS METRICS
            </div>
            <div style="font-family: 'VT323', monospace; font-size: 19px;
                        color: {Y2K_COLORS['text_main']}; line-height: 1.8;">
                <span style="color: {Y2K_COLORS['text_dim']};">Model:</span> <strong style="color: {Y2K_COLORS['accent_primary']};">{model}</strong><br>
                <span style="color: {Y2K_COLORS['text_dim']};">Input Tokens:</span> <strong>{input_tokens:,}</strong><br>
                <span style="color: {Y2K_COLORS['text_dim']};">Output Tokens:</span> <strong>{output_tokens:,}</strong><br>
                <span style="color: {Y2K_COLORS['text_dim']};">Est. Cost:</span> <strong style="color: {Y2K_COLORS['accent_tertiary']};">¥{cost:.4f}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cover_preview(cover_url: str, title: str):
    """渲染封面图预览（通过后端下载绕过防盗链）"""
    if not cover_url:
        return

    try:
        headers = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        resp = requests.get(cover_url, headers=headers, timeout=10)
        resp.raise_for_status()

        img_b64 = base64.b64encode(resp.content).decode("utf-8")
        mime = "image/jpeg"
        if resp.content[:4] == b"\x89PNG":
            mime = "image/png"
        elif resp.content[:3] == b"GIF":
            mime = "image/gif"
        elif resp.content[:4] == b"RIFF":
            mime = "image/webp"
        data_url = f"data:{mime};base64,{img_b64}"

        st.markdown(
            f"""
            <div style="
                border: 2px solid {Y2K_COLORS['accent_secondary']};
                box-shadow: 0 0 16px rgba(255, 42, 109, 0.15);
                padding: 4px;
                display: inline-block;
                margin: 10px 0;
                background: {Y2K_COLORS['bg_card']};
                position: relative;
            ">
                <img src="{data_url}" alt="{title}"
                     style="max-width: 340px; width: 100%; display: block;
                            filter: saturate(1.2) contrast(1.05);">
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.markdown(
            f"""
            <div style="
                border: 2px solid {Y2K_COLORS['accent_secondary']};
                border-left: 4px solid {Y2K_COLORS['error']};
                padding: 16px;
                margin: 10px 0;
                background: {Y2K_COLORS['bg_card']};
                font-family: 'VT323', monospace;
                font-size: 18px;
                color: {Y2K_COLORS['accent_secondary']};
            ">
                封面加载失败: {str(e)[:80]}<br>
                <a href="{cover_url}" target="_blank"
                   style="color: {Y2K_COLORS['accent_primary']};">
                   点击直接查看封面
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _hex_to_rgb(hex_color: str) -> str:
    """将 #RRGGBB 转为 'r, g, b' 字符串用于 rgba()"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"
