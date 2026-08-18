"""BiliDecode 配置常量"""

# ─── 百炼 API ───
BAILIAN_API_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

BAILIAN_MODELS = {
    "qwen3-vl-plus": {
        "label": "qwen3-vl-plus (推荐·多模态)",
        "multimodal": True,
        "input_price": 1.0,      # 元/百万tokens (≤32K)
        "output_price": 10.0,    # 元/百万tokens
        "max_tokens": 4096,
        "temperature": 0.7,
        "context_length": 262144,
    },
    "qwen-plus": {
        "label": "qwen-plus (低成本·纯文本)",
        "multimodal": False,
        "input_price": 0.8,
        "output_price": 2.0,
        "max_tokens": 4096,
        "temperature": 0.7,
        "context_length": 131072,
    },
}

DEFAULT_MODEL = "qwen3-vl-plus"

# ─── B站 API 端点 ───
BILIBILI_API = {
    "video_info": "https://api.bilibili.com/x/web-interface/view",
    "video_tags": "https://api.bilibili.com/x/tag/archive/tags",
    "comments": "https://api.bilibili.com/x/v2/reply",
    "danmaku": "https://comment.bilibili.com/{cid}.xml",
    "owner_info": "https://api.bilibili.com/x/space/acc/info",
    "owner_stat": "https://api.bilibili.com/x/relation/stat",
}

BILIBILI_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com",
}

# ─── 请求参数 ───
REQUEST_TIMEOUT = 10          # 秒
REQUEST_INTERVAL = 0.5        # 请求间隔（秒）
MAX_RETRIES = 2               # API 调用失败重试次数
RETRY_DELAY = 3               # 重试间隔（秒）
MODEL_TIMEOUT = 120           # 模型调用超时（秒）

# ─── 数据采集参数 ───
HOT_COMMENT_LIMIT = 20        # 热评数量
DANMAKU_LIMIT = 50            # 高频弹幕数量

# ─── Y2K 配色 ───
Y2K_COLORS = {
    "bg_main": "#0D0221",        # 更深的暗紫底色
    "bg_card": "#1A0B2E",        # 卡片背景（暗色系）
    "bg_card_light": "#F0F0F0",  # 折叠面板浅底
    "accent_primary": "#00F0FF",   # 电光青
    "accent_secondary": "#FF2A6D", # 霓虹品红
    "accent_tertiary": "#FFD700",  # 金色点缀
    "text_main": "#E8E8FF",       # 主文字（淡紫白）
    "text_dim": "#8B8BA7",        # 次要文字
    "success": "#39FF14",         # 荧光绿
    "error": "#FF0040",           # 警示红
    "warning": "#FFD700",         # 警告金
    "border": "#2D1B4E",          # 暗紫边框
    "border_bright": "#00F0FF",   # 亮色边框
}

Y2K_FONTS = {
    "title": "'Press Start 2P', cursive",
    "body": "'VT323', monospace",
}

# ─── Google Fonts ───
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Press+Start+2P&family=VT323&family=Silkscreen:wght@400;700&display=swap"
)

# ─── Waffo Pancake 支付 ───
WAFFO_API_BASE = "https://api.waffo.ai"
