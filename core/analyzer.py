"""模型调用模块 —— 封装百炼 API 调用，支持多模态（封面图+文本）和纯文本两种模式"""

import time
import os
from dataclasses import dataclass

import httpx
from openai import OpenAI

from config import (
    BAILIAN_API_BASE_URL,
    BAILIAN_MODELS,
    MAX_RETRIES,
    RETRY_DELAY,
    MODEL_TIMEOUT,
)
from core.bilibili_client import VideoData
from core.prompts import build_prompt


@dataclass
class AnalysisResult:
    text: str = ""               # 模型输出的 Markdown 报告
    input_tokens: int = 0        # 输入 token 数
    output_tokens: int = 0       # 输出 token 数
    model: str = ""              # 使用的模型名称
    multimodal: bool = False     # 是否使用了封面图
    estimated_cost: float = 0.0  # 预估费用（元）
    error: str = ""              # 错误信息（成功时为空）


def _create_client(api_key: str) -> OpenAI:
    """创建 OpenAI 兼容客户端，绕过代理直连百炼 API"""
    _http = httpx.Client(trust_env=False)
    return OpenAI(
        api_key=api_key,
        base_url=BAILIAN_API_BASE_URL,
        timeout=MODEL_TIMEOUT,
        http_client=_http,
    )


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """根据模型定价和 token 用量计算费用（元）"""
    model_info = BAILIAN_MODELS.get(model)
    if not model_info:
        return 0.0
    input_cost = (input_tokens / 1_000_000) * model_info["input_price"]
    output_cost = (output_tokens / 1_000_000) * model_info["output_price"]
    return round(input_cost + output_cost, 4)


def analyze_video_metadata(
    video_data: VideoData,
    model: str = "qwen3-vl-plus",
    api_key: str = None,
) -> AnalysisResult:
    """
    调用百炼模型分析视频公开元数据。

    对于多模态模型，封面图 URL 作为 image_url 与文本提示词组合传入。
    对于纯文本模型，仅传入文本提示词。

    返回 AnalysisResult，包含分析文本、token 用量、预估费用。
    """
    result = AnalysisResult(model=model)

    # 获取 API Key
    if not api_key:
        api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        result.error = "服务端未配置 DASHSCOPE_API_KEY，请联系管理员"
        return result

    # 获取模型配置
    model_info = BAILIAN_MODELS.get(model)
    if not model_info:
        result.error = f"未知模型：{model}"
        return result

    result.multimodal = model_info["multimodal"]

    # 构造提示词
    system_prompt, user_prompt = build_prompt(video_data)

    # 组装消息内容
    content = []

    # 封面图（仅多模态模型且有封面 URL）
    if model_info["multimodal"] and video_data.cover_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": video_data.cover_url},
        })

    # 文本提示词
    content.append({"type": "text", "text": user_prompt})

    # 调用 API（带重试）
    client = _create_client(api_key)

    for attempt in range(MAX_RETRIES + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content},
                ],
                max_tokens=model_info["max_tokens"],
                temperature=model_info["temperature"],
            )

            result.text = completion.choices[0].message.content or ""
            usage = completion.usage
            if usage:
                result.input_tokens = usage.prompt_tokens
                result.output_tokens = usage.completion_tokens
            result.estimated_cost = _estimate_cost(
                model, result.input_tokens, result.output_tokens
            )
            return result

        except Exception as e:
            error_msg = str(e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            result.error = f"模型调用失败（重试 {MAX_RETRIES} 次后仍报错）：{error_msg}"
            return result

    result.error = "模型调用失败：达到最大重试次数"
    return result
