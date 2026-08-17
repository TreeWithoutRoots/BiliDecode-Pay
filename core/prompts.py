"""提示词构造 —— 系统角色设定 + 用户提示词模板"""

import time

from core.bilibili_client import VideoData


SYSTEM_PROMPT = """\
你是一位首席内容策略官兼爆款解码师，擅长从视频的外部数据信号中推理内容价值与传播逻辑。

你的分析依据是B站视频的公开元数据：标题、简介、标签、互动统计（播放/点赞/投币/收藏/转发/弹幕）、热门评论、高频弹幕、UP主信息以及封面图。你不具备视频实际画面和音频内容，所有关于视频内部内容的判断均为基于外部信号的推测。

分析原则：
1. 区分"数据事实"和"推测判断"。数据事实直接引用指标数值，推测判断需标注依据和置信度。
2. 互动率 = (点赞 + 投币 + 收藏 + 评论) / 播放量。收藏率高通常意味着实用型内容，互动率低但播放量高可能意味着标题党。
3. 评论和弹幕是观众情绪的直接信号，重点分析情感倾向和核心话题。
4. 封面图是视频的第一视觉印象，分析其设计策略和对目标受众的吸引力。
5. 所有建议必须具体可落地，避免空泛的"提升内容质量"之类的废话。

输出格式为 Markdown，严格按以下六个维度展开，每个维度用二级标题分隔。\
"""


def build_user_prompt(vd: VideoData) -> str:
    """将 VideoData 中的字段组装为结构化用户提示词。"""

    # 基本信息
    duration_min = f"{vd.duration // 60}分{vd.duration % 60}秒" if vd.duration else "未知"
    pub_date = (
        time.strftime("%Y-%m-%d", time.localtime(vd.pubdate))
        if vd.pubdate
        else "未知"
    )

    # 热门评论格式化
    if vd.hot_comments:
        comment_lines = []
        for i, c in enumerate(vd.hot_comments[:10], 1):
            comment_lines.append(
                f"  {i}. [{c.username}] {c.content} (赞:{c.like_count} 回复:{c.reply_count})"
            )
        comments_text = "\n".join(comment_lines)
    else:
        comments_text = "  （无评论数据）"

    # 弹幕格式化
    if vd.top_danmaku:
        danmaku_text = "、".join(vd.top_danmaku[:20])
    else:
        danmaku_text = "（无弹幕数据）"

    # 标签
    tags_text = "、".join(vd.tags) if vd.tags else "（无标签数据）"

    # 采集错误
    errors_text = ""
    if vd.errors:
        errors_text = "\n\n⚠ 数据采集异常：\n" + "\n".join(f"- {e}" for e in vd.errors)

    prompt = f"""\
请分析以下B站视频的公开元数据，并按六个维度输出结构化分析报告。

## 视频基本信息
- 标题：{vd.title}
- 简介：{vd.desc or '（无简介）'}
- BV号：{vd.bvid}
- 分区：{vd.category}
- 时长：{duration_min}
- 发布日期：{pub_date}
- 标签：{tags_text}

## 互动统计数据
- 播放量：{vd.stat_view:,}
- 点赞：{vd.stat_like:,}
- 投币：{vd.stat_coin:,}
- 收藏：{vd.stat_favorite:,}
- 转发：{vd.stat_share:,}
- 评论数：{vd.stat_reply:,}
- 弹幕数：{vd.stat_danmaku:,}

## UP主信息
- 名称：{vd.owner_name}
- 等级：Lv{vd.owner_level}
- 粉丝数：{vd.owner_fans:,}

## 热门评论（前10条）
{comments_text}

## 高频弹幕
{danmaku_text}
{errors_text}

---

请严格按以下格式输出分析报告，使用 Markdown：

## 一、视频总览表

以表格呈现核心指标和一句话洞察：

| 指标 | 数值 | 互动率/占比 | 洞察 |
|------|------|------------|------|
（填入播放量、互动率、点赞率、投币率、收藏率、弹幕密度等，最后一列为简短洞察）

## 二、内容主题分析

基于标题、简介、标签、封面图推断视频主题与目标受众。分析标题的关键词策略和吸引力，评价封面的视觉传达效果。

## 三、互动数据分析

计算各项互动率，与B站常规基准对比（普通视频互动率约3-8%）。分析互动结构是否健康，判断内容类型（娱乐型/实用型/情感型等）。

## 四、评论情感分析

对热门评论进行情感分类（正面/中性/负面），提取高频话题关键词，总结观众核心反馈和情绪倾向。

## 五、UP主画像分析

基于等级、粉丝数、本视频数据，分析创作者影响力和内容策略定位。

## 六、爆款归因与建议

综合以上维度，推理视频传播表现的核心驱动因素，给出3条可复用的内容创作建议。每条建议需具体、可落地。
"""

    return prompt


def build_prompt(vd: VideoData) -> tuple[str, str]:
    """构造完整的系统提示词和用户提示词。"""
    return SYSTEM_PROMPT, build_user_prompt(vd)
