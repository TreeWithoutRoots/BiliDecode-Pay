# BiliDecode — B站视频分析终端

Y2K 像素风格的 B站视频公开元数据分析工具。输入 B站视频链接，系统采集公开元数据（标题、统计、评论、弹幕、封面等），调用阿里百炼多模态大模型生成六维度结构化分析报告。

## 功能

- 通过 B站公开 API 采集视频元数据（标题、简介、标签、播放/点赞/投币/收藏/转发/弹幕数）
- 采集前 20 条热门评论和前 50 条高频弹幕
- 采集 UP主信息（等级、粉丝数）
- 将封面图 + 文本元数据送入百炼多模态大模型分析
- 输出六维度报告：总览表、内容主题、互动数据、评论情感、UP主画像、爆款归因
- Y2K 像素风 UI（Press Start 2P + VT323 字体，霓虹粉/暗青色配色）

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd BiliDecode

# 安装依赖
pip install -r requirements.txt
```

## 配置（项目方部署）

API Key 由项目方在服务端配置，终端用户无需提供。

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env`，填入百炼 API Key：
```
DASHSCOPE_API_KEY=sk-your-actual-key
```

API Key 获取地址：https://bailian.console.aliyun.com/

> `.env` 已在 `.gitignore` 中忽略，不会提交到仓库。云端部署时也可通过 Streamlit Cloud Secrets 或环境变量注入。

## 运行

```bash
streamlit run app.py
```

浏览器访问 http://localhost:8501

## 支持的链接格式

- 标准链接：`https://www.bilibili.com/video/BV1xx411c7mD`
- 短链接：`https://b23.tv/xxxxxxx`
- 移动端：`https://m.bilibili.com/video/BV1xx411c7mD`

## 模型选择

| 模型 | 特点 | 输入价格 | 输出价格 |
|------|------|----------|----------|
| qwen3-vl-plus | 多模态，支持封面图分析 | 1 元/百万tokens | 10 元/百万tokens |
| qwen-plus | 纯文本，成本最低 | 0.8 元/百万tokens | 2 元/百万tokens |

单次分析成本约 0.02-0.05 元。

## 项目结构

```
├── app.py                 # Streamlit 主应用
├── config.py              # 配置常量
├── core/
│   ├── bilibili_client.py # B站公开 API 封装
│   ├── analyzer.py        # 百炼模型调用
│   └── prompts.py         # 提示词模板
├── ui/
│   ├── style.py           # Y2K CSS
│   └── components.py      # 自定义组件
├── utils/
│   └── url_parser.py      # URL 解析
├── .env.example           # 环境变量模板
└── requirements.txt       # 依赖清单
```

## 合规说明

本项目仅采集 B站页面上公开展示的元数据（无需登录即可查看的信息），不下载、不存储、不传播视频内容。所有数据采集通过 B站 Web API 完成，仅用于个人学习研究目的。
