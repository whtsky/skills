#!/usr/bin/env bash
# bilibili.sh - 获取B站视频内容（字幕 → 音频转写 fallback）
# Usage: bilibili.sh <url_or_bvid> [--info-only|--subtitle-only]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

info() { echo "[INFO] $*" >&2; }
warn() { echo "[WARN] $*" >&2; }
error() { echo "[ERROR] $*" >&2; }

get_sessdata() {
    # Only use environment variable
    if [[ -n "${BILIBILI_SESSDATA:-}" ]]; then
        echo "$BILIBILI_SESSDATA"
        return
    fi
    echo ""
}

# 从URL提取BV号
extract_bvid() {
    local input="$1"
    if [[ "$input" =~ (BV[a-zA-Z0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi
    if [[ "$input" =~ b23\.tv ]]; then
        local expanded
        expanded=$(curl -sLI "$input" 2>/dev/null | grep -i '^location:' | tail -1 | tr -d '\r')
        if [[ "$expanded" =~ (BV[a-zA-Z0-9]+) ]]; then
            echo "${BASH_REMATCH[1]}"
            return 0
        fi
    fi
    error "无法提取BV号: $input"
    return 1
}

api_call() {
    local url="$1"
    local sessdata
    sessdata=$(get_sessdata)
    local headers=(-H "Referer: https://www.bilibili.com" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    [[ -n "$sessdata" ]] && headers+=(-H "Cookie: SESSDATA=$sessdata")
    curl -s "${headers[@]}" "$url"
}

# 尝试获取字幕
try_subtitle() {
    local aid="$1" cid="$2"
    local player_resp
    player_resp=$(api_call "https://api.bilibili.com/x/player/v2?aid=$aid&cid=$cid")

    local subtitle_count
    subtitle_count=$(echo "$player_resp" | jq '.data.subtitle.subtitles | length')

    if [[ "$subtitle_count" -gt 0 ]]; then
        local subtitle_url
        subtitle_url=$(echo "$player_resp" | jq -r '
            .data.subtitle.subtitles |
            (map(select(.lan | startswith("ai-") | not)) | first) //
            (first) |
            .subtitle_url // empty
        ')
        if [[ -n "$subtitle_url" ]]; then
            [[ "$subtitle_url" == //* ]] && subtitle_url="https:$subtitle_url"
            api_call "$subtitle_url" | jq -r '.body[].content' 2>/dev/null
            return 0
        fi
    fi

    local need_login
    need_login=$(echo "$player_resp" | jq -r '.data.need_login_subtitle // false')
    if [[ "$need_login" == "true" ]]; then
        warn "有字幕但需要登录（cookie可能过期或未配置）"
    else
        warn "该视频没有字幕"
    fi
    return 1
}

# 通过API下载音频（绕过yt-dlp的412问题）
download_audio_via_api() {
    local bvid="$1" cid="$2" output_dir="$3"

    # 获取音频流URL (fnval=16 = dash格式)
    local playurl_resp
    playurl_resp=$(api_call "https://api.bilibili.com/x/player/playurl?bvid=$bvid&cid=$cid&qn=16&fnval=16")

    local code
    code=$(echo "$playurl_resp" | jq -r '.code')
    if [[ "$code" != "0" ]]; then
        warn "playurl API 错误: $code"
        return 1
    fi

    # 取最低质量的音频流
    local audio_url
    audio_url=$(echo "$playurl_resp" | jq -r '.data.dash.audio | sort_by(.bandwidth) | first | .baseUrl // empty')

    if [[ -z "$audio_url" ]]; then
        warn "无法获取音频流URL"
        return 1
    fi

    local sessdata
    sessdata=$(get_sessdata)
    local output_file="$output_dir/audio.m4a"

    info "正在下载音频流..."
    local dl_headers=(-H "Referer: https://www.bilibili.com" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    [[ -n "$sessdata" ]] && dl_headers+=(-H "Cookie: SESSDATA=$sessdata")

    curl -sL "${dl_headers[@]}" -o "$output_file" "$audio_url"

    local file_size
    file_size=$(stat -c%s "$output_file" 2>/dev/null || stat -f%z "$output_file" 2>/dev/null)
    if [[ "$file_size" -lt 1000 ]]; then
        warn "下载的音频文件过小 (${file_size}B)，可能失败"
        return 1
    fi

    info "音频下载完成: $((file_size / 1024))KB"
    echo "$output_file"
}

# === Main ===
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <bilibili_url_or_bvid> [--info-only|--subtitle-only]" >&2
    exit 1
fi

INPUT="$1"
MODE="${2:-}"

BVID=$(extract_bvid "$INPUT")
info "BV号: $BVID"

# 获取视频信息
VIDEO_INFO=$(api_call "https://api.bilibili.com/x/web-interface/view?bvid=$BVID")
CODE=$(echo "$VIDEO_INFO" | jq -r '.code')

if [[ "$CODE" != "0" ]]; then
    MSG=$(echo "$VIDEO_INFO" | jq -r '.message // "未知错误"')
    error "API错误 ($CODE): $MSG"
    exit 1
fi

TITLE=$(echo "$VIDEO_INFO" | jq -r '.data.title')
AUTHOR=$(echo "$VIDEO_INFO" | jq -r '.data.owner.name')
DURATION=$(echo "$VIDEO_INFO" | jq -r '.data.duration')
AID=$(echo "$VIDEO_INFO" | jq -r '.data.aid')
CID=$(echo "$VIDEO_INFO" | jq -r '.data.cid // .data.pages[0].cid')
DESC=$(echo "$VIDEO_INFO" | jq -r '.data.desc // ""')
VIEW=$(echo "$VIDEO_INFO" | jq -r '.data.stat.view // 0')

info "标题: $TITLE"
info "UP主: $AUTHOR | 时长: ${DURATION}s | 播放: $VIEW"

echo "# $TITLE"
echo "UP主: $AUTHOR | 时长: $((DURATION/60))分$((DURATION%60))秒 | 播放: $VIEW"
[[ -n "$DESC" && "$DESC" != "-" && "$DESC" != "null" ]] && echo "简介: $DESC"
echo "---"
echo ""

[[ "$MODE" == "--info-only" ]] && exit 0

# 尝试字幕
if try_subtitle "$AID" "$CID"; then
    info "成功获取字幕"
    exit 0
fi

[[ "$MODE" == "--subtitle-only" ]] && { warn "字幕获取失败"; exit 1; }

# Fallback: 通过API下载音频 → Groq Whisper转写
if [[ -z "${GROQ_WHISPER_SCRIPT:-}" ]]; then
    error "请设置 GROQ_WHISPER_SCRIPT 环境变量指向 groq-whisper 转写脚本"
    exit 1
fi

if [[ ! -x "$GROQ_WHISPER_SCRIPT" ]]; then
    error "groq-whisper script 不存在或不可执行: $GROQ_WHISPER_SCRIPT"
    exit 1
fi

info "字幕不可用，尝试音频转写..."

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

AUDIO_FILE=$(download_audio_via_api "$BVID" "$CID" "$TMPDIR")
if [[ -z "$AUDIO_FILE" ]]; then
    error "音频下载失败"
    exit 1
fi

bash "$GROQ_WHISPER_SCRIPT" "$AUDIO_FILE" --lang zh
