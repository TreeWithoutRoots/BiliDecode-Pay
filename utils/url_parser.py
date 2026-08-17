"""B站 URL 解析与校验"""

import re
import requests
from config import BILIBILI_HEADERS, REQUEST_TIMEOUT


# BV号正则：BV开头 + 10位字母数字
BV_PATTERN = re.compile(r"BV[0-9A-Za-z]{10}")


def extract_bvid(url: str) -> str | None:
    """
    从B站 URL 中提取 BV 号。
    支持三种格式：
      - 标准链接：https://www.bilibili.com/video/BV1xx411c7mD
      - 短链接：  https://b23.tv/xxxxxxx （需 HTTP 重定向解析）
      - 移动端：  https://m.bilibili.com/video/BV1xx411c7mD
    返回 BV 号字符串，解析失败返回 None。
    """
    url = url.strip()
    if not url:
        return None

    # 直接从 URL 中匹配 BV 号
    match = BV_PATTERN.search(url)
    if match:
        return match.group()

    # 短链接 b23.tv 需要跟随重定向
    if "b23.tv" in url:
        try:
            resp = requests.get(
                url,
                headers=BILIBILI_HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            match = BV_PATTERN.search(resp.url)
            if match:
                return match.group()
        except requests.RequestException:
            return None

    return None


def validate_bvid(bvid: str) -> bool:
    """校验 BV 号格式合法性"""
    if not bvid:
        return False
    return bool(BV_PATTERN.fullmatch(bvid))


def parse_url(url: str) -> str | None:
    """
    解析B站 URL，返回合法的 BV 号。
    无效 URL 返回 None。
    """
    bvid = extract_bvid(url)
    if bvid and validate_bvid(bvid):
        return bvid
    return None
