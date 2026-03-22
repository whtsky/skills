---
name: bilibili
description: Extract and transcribe Bilibili (B站) video content via subtitles or Groq Whisper audio transcription for summarization and analysis.
compatibility: "Requires bash, curl, jq, BILIBILI_SESSDATA. Optional: yt-dlp and Groq API for audio transcription fallback."
metadata:
  category: media
  region: cn
  tags: video, transcription, subtitles, bilibili, china
---

# Bilibili 视频内容获取

获取B站视频的文字内容，用于理解和总结视频。

## 使用方法

```bash
# 获取视频内容（先尝试字幕，失败则音频转写）
bash scripts/bilibili.sh "https://www.bilibili.com/video/BV1xx..."

# 只获取视频信息（标题、UP主、时长等）
bash scripts/bilibili.sh "BV1xx..." --info-only

# 只尝试字幕（不fallback到音频转写）
bash scripts/bilibili.sh "BV1xx..." --subtitle-only
```

支持的输入格式：
- 完整链接：`https://www.bilibili.com/video/BVxxx`
- BV号：`BV1xx411c7mD`
- 短链接：`https://b23.tv/xxx`

## 工作流程

1. 通过 API 获取视频信息（标题、UP主、时长）
2. 尝试获取 CC 字幕或 AI 字幕（优先 CC）
3. 如果字幕不可用，用 yt-dlp 下载音频 + groq-whisper 转写

## 配置

Set the following environment variables:

```bash
export BILIBILI_SESSDATA="your-bilibili-sessdata"
export GROQ_API_KEY="your-groq-api-key"  
export GROQ_WHISPER_SCRIPT="/path/to/groq-whisper/transcribe.sh"
```

- **BILIBILI_SESSDATA**: B站会话cookie，用于访问字幕和下载音频
- **GROQ_API_KEY**: Groq API密钥，用于音频转写（音频fallback需要）
- **GROQ_WHISPER_SCRIPT**: groq-whisper转写脚本的绝对路径

## 输出格式

```
# 视频标题
UP主: xxx | 时长: x分x秒
---

（字幕文本或转写文本）
```

## 限制

- 没有 BILIBILI_SESSDATA 时：字幕大概率获取不到，音频下载也会被拒绝
- Cookie 有效期约几个月，过期需要更新
- 番剧可能有地域限制
