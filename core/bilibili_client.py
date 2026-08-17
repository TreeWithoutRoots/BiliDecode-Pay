"""B站公开 API 封装 —— 采集视频元数据、评论、弹幕、UP主信息"""

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import requests

from config import (
    BILIBILI_API,
    BILIBILI_HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_INTERVAL,
    MAX_RETRIES,
    HOT_COMMENT_LIMIT,
    DANMAKU_LIMIT,
)


@dataclass
class Comment:
    content: str
    like_count: int
    username: str
    reply_count: int = 0


@dataclass
class VideoData:
    bvid: str = ""
    aid: int = 0
    cid: int = 0
    title: str = ""
    desc: str = ""
    cover_url: str = ""
    duration: int = 0          # 秒
    pubdate: int = 0           # 时间戳
    category: str = ""
    tags: list[str] = field(default_factory=list)
    owner_name: str = ""
    owner_mid: int = 0
    owner_level: int = 0
    owner_fans: int = 0
    stat_view: int = 0
    stat_like: int = 0
    stat_coin: int = 0
    stat_favorite: int = 0
    stat_share: int = 0
    stat_reply: int = 0
    stat_danmaku: int = 0
    hot_comments: list[Comment] = field(default_factory=list)
    top_danmaku: list[str] = field(default_factory=list)
    # 采集状态标记
    errors: list[str] = field(default_factory=list)


def _request(url: str, params: dict = None) -> dict | None:
    """发起 GET 请求，带重试。返回 JSON dict 或 None。"""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                params=params,
                headers=BILIBILI_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data")
            else:
                return None
        except (requests.RequestException, ValueError):
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_INTERVAL)
            else:
                return None
    return None


def _request_raw(url: str) -> str | None:
    """发起 GET 请求，返回原始文本（用于弹幕 XML）。"""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                headers=BILIBILI_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_INTERVAL)
            else:
                return None
    return None


def get_video_info(bvid: str) -> dict | None:
    """获取视频基本信息：标题、简介、封面、统计、时长、分区、cid 等。"""
    return _request(BILIBILI_API["video_info"], params={"bvid": bvid})


def get_video_tags(bvid: str) -> list[str]:
    """获取视频标签列表。"""
    data = _request(BILIBILI_API["video_tags"], params={"bvid": bvid})
    if data and isinstance(data, list):
        return [tag.get("tag_name", "") for tag in data if tag.get("tag_name")]
    return []


def get_hot_comments(aid: int, limit: int = HOT_COMMENT_LIMIT) -> list[Comment]:
    """获取热门评论（按热度排序）。"""
    data = _request(
        BILIBILI_API["comments"],
        params={
            "type": 1,
            "oid": aid,
            "pn": 1,
            "ps": limit,
            "sort": 1,  # 按热度
        },
    )
    if not data:
        return []

    comments = []
    replies = data.get("replies", [])
    for r in replies[:limit]:
        content_msg = r.get("content", {})
        message = content_msg.get("message", "")
        like = r.get("like", 0)
        member = r.get("member", {})
        uname = member.get("uname", "匿名用户")
        rcount = r.get("rcount", 0)
        if message:
            comments.append(Comment(
                content=message,
                like_count=like,
                username=uname,
                reply_count=rcount,
            ))
    return comments


def get_top_danmaku(cid: int, limit: int = DANMAKU_LIMIT) -> list[str]:
    """获取高频弹幕（从 XML 中提取，按出现频率排序）。"""
    url = BILIBILI_API["danmaku"].format(cid=cid)
    xml_text = _request_raw(url)
    if not xml_text:
        return []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    # 统计弹幕出现频率
    freq: dict[str, int] = {}
    for d in root.findall("d"):
        if d.text:
            text = d.text.strip()
            if text:
                freq[text] = freq.get(text, 0) + 1

    # 按频率排序，取前 limit 条
    sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [text for text, count in sorted_items[:limit]]


def get_owner_info(mid: int) -> tuple[int, int]:
    """获取 UP主信息：返回 (等级, 粉丝数)。失败返回 (0, 0)。"""
    level = 0
    fans = 0

    # 用户基础信息（含等级）
    data = _request(BILIBILI_API["owner_info"], params={"mid": mid})
    if data:
        level = data.get("level", 0)

    time.sleep(REQUEST_INTERVAL)

    # 粉丝数
    stat_data = _request(BILIBILI_API["owner_stat"], params={"vmid": mid})
    if stat_data:
        fans = stat_data.get("follower", 0)

    return level, fans


def fetch_video_data(bvid: str) -> VideoData:
    """
    采集视频全部公开数据，返回 VideoData。
    单个采集步骤失败时记录错误但不中断流程。
    """
    vd = VideoData(bvid=bvid)

    # 1. 视频基本信息
    info = get_video_info(bvid)
    if not info:
        vd.errors.append("视频信息获取失败（视频可能不存在或已被删除）")
        return vd

    vd.aid = info.get("aid", 0)
    vd.cid = info.get("cid", 0)
    vd.title = info.get("title", "")
    vd.desc = info.get("desc", "")
    vd.cover_url = info.get("pic", "")
    vd.duration = info.get("duration", 0)
    vd.pubdate = info.get("pubdate", 0)

    owner = info.get("owner", {})
    vd.owner_name = owner.get("name", "")
    vd.owner_mid = owner.get("mid", 0)

    stat = info.get("stat", {})
    vd.stat_view = stat.get("view", 0)
    vd.stat_like = stat.get("like", 0)
    vd.stat_coin = stat.get("coin", 0)
    vd.stat_favorite = stat.get("favorite", 0)
    vd.stat_share = stat.get("share", 0)
    vd.stat_reply = stat.get("reply", 0)
    vd.stat_danmaku = stat.get("danmaku", 0)

    # 分区名
    tid = info.get("tid", 0)
    tname = info.get("tname", "")
    vd.category = tname if tname else f"分区ID:{tid}"

    time.sleep(REQUEST_INTERVAL)

    # 2. 标签
    tags = get_video_tags(bvid)
    if tags:
        vd.tags = tags
    else:
        vd.errors.append("标签获取失败")

    time.sleep(REQUEST_INTERVAL)

    # 3. 热门评论
    if vd.aid:
        comments = get_hot_comments(vd.aid)
        if comments:
            vd.hot_comments = comments
        else:
            vd.errors.append("评论获取失败或无评论")
    else:
        vd.errors.append("缺少 aid，跳过评论采集")

    time.sleep(REQUEST_INTERVAL)

    # 4. 弹幕
    if vd.cid:
        danmaku = get_top_danmaku(vd.cid)
        if danmaku:
            vd.top_danmaku = danmaku
        else:
            vd.errors.append("弹幕获取失败或无弹幕")
    else:
        vd.errors.append("缺少 cid，跳过弹幕采集")

    time.sleep(REQUEST_INTERVAL)

    # 5. UP主信息
    if vd.owner_mid:
        level, fans = get_owner_info(vd.owner_mid)
        vd.owner_level = level
        vd.owner_fans = fans
        if level == 0 and fans == 0:
            vd.errors.append("UP主信息获取失败")
    else:
        vd.errors.append("缺少 mid，跳过UP主信息采集")

    return vd
