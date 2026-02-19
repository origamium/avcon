#!/usr/bin/env bash
# ==============================================================================
# collect_samples.sh — DENON AVC-A110 API サンプル収集スクリプト
#
# 使い方:
#   ./tools/collect_samples.sh <sample_name> [--ip IP] [--mask]
#
# 例:
#   ./tools/collect_samples.sh F1_DD+_Atmos
#   ./tools/collect_samples.sh F1_DD+_Atmos --mask
#   ./tools/collect_samples.sh F1_DD+_Atmos --ip 192.168.1.100 --mask
# ==============================================================================
set -euo pipefail

# --- 色定義 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# --- ステータス出力ヘルパー ---
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

# --- 定数 ---
PORT=8080
TIMEOUT=5
STATUS_LITE_PATH="/goform/formMainZone_MainZoneXmlStatusLite.xml"
APPCOMMAND_PATH="/goform/AppCommand.xml"
APPCOMMAND0300_PATH="/goform/AppCommand0300.xml"

# --- プロジェクトルートを特定 ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- 使い方表示 ---
usage() {
    echo "使い方: $0 <sample_name> [--ip IP] [--mask]"
    echo ""
    echo "引数:"
    echo "  sample_name   サンプル名 (例: F1_DD+_Atmos)"
    echo "  --ip IP       AVR の IP アドレス (省略時は .env の D_AVAMP_IP を使用)"
    echo "  --mask        個人情報 (IP, MAC, SSID) をマスクする"
    exit 1
}

# --- 引数パース ---
SAMPLE_NAME=""
AVR_IP=""
MASK=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ip)
            [[ $# -lt 2 ]] && { fail "--ip にはIPアドレスが必要です"; exit 1; }
            AVR_IP="$2"
            shift 2
            ;;
        --mask)
            MASK=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        -*)
            fail "不明なオプション: $1"
            usage
            ;;
        *)
            if [[ -z "$SAMPLE_NAME" ]]; then
                SAMPLE_NAME="$1"
            else
                fail "サンプル名が2つ以上指定されています"
                usage
            fi
            shift
            ;;
    esac
done

[[ -z "$SAMPLE_NAME" ]] && { fail "サンプル名を指定してください"; usage; }

# --- .env から IP を取得 (--ip 未指定時) ---
if [[ -z "$AVR_IP" ]]; then
    ENV_FILE="$PROJECT_ROOT/.env"
    if [[ -f "$ENV_FILE" ]]; then
        AVR_IP=$(grep -E '^D_AVAMP_IP=' "$ENV_FILE" | cut -d'=' -f2 | tr -d '[:space:]')
    fi
    if [[ -z "$AVR_IP" ]]; then
        fail ".env に D_AVAMP_IP が設定されていないか、--ip で指定してください"
        exit 1
    fi
fi

# --- 出力先の準備 ---
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TIMESTAMP_HUMAN=$(date '+%Y-%m-%d %H:%M:%S')
SAMPLES_DIR="$PROJECT_ROOT/samples"
mkdir -p "$SAMPLES_DIR"
OUTPUT_FILE="$SAMPLES_DIR/${SAMPLE_NAME}_${TIMESTAMP}.xml"

ok "サンプル名: $SAMPLE_NAME"
ok "AVR IP: $AVR_IP"
ok "出力先: $OUTPUT_FILE"
[[ "$MASK" == true ]] && warn "マスクモード有効"
echo ""

# --- 接続チェック ---
echo "接続チェック中..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$TIMEOUT" \
    "http://${AVR_IP}:${PORT}${STATUS_LITE_PATH}" 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" != "200" ]]; then
    fail "AVR に接続できません (HTTP $HTTP_CODE)"
    fail "  URL: http://${AVR_IP}:${PORT}${STATUS_LITE_PATH}"
    exit 1
fi
ok "AVR 接続確認 (HTTP $HTTP_CODE)"
echo ""

# ==============================================================================
# curl ヘルパー: POST XML を送信してレスポンスを返す
# ==============================================================================
post_xml() {
    local url="$1"
    local body="$2"
    curl -s --connect-timeout "$TIMEOUT" -m 10 \
        -H "Content-Type: text/xml; charset=utf-8" \
        -d "$body" \
        "$url" 2>/dev/null || echo ""
}

# ==============================================================================
# マスク処理
# ==============================================================================
apply_mask() {
    local content="$1"
    if [[ "$MASK" == true ]]; then
        # AVR IP をマスク
        content=$(echo "$content" | sed "s/${AVR_IP}/XXX.XXX.XXX.XXX/g")
        # MAC アドレスをマスク (XX:XX:XX:XX:XX:XX パターン)
        content=$(echo "$content" | sed -E 's/[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}/XX:XX:XX:XX:XX:XX/g')
        # SSID をマスク (<SSID>値</SSID> → <SSID>&lt;SSID&gt;</SSID>)
        content=$(echo "$content" | sed -E 's|(<SSID[^>]*>)[^<]+(</SSID>)|\1\&lt;SSID\&gt;\2|g')
        # ssid タグ小文字版も
        content=$(echo "$content" | sed -E 's|(<ssid[^>]*>)[^<]+(</ssid>)|\1\&lt;SSID\&gt;\2|g')
    fi
    echo "$content"
}

# ==============================================================================
# 出力ファイルにセクションを書き込む
# ==============================================================================
write_section() {
    local title="$1"
    local content="$2"
    {
        echo ""
        echo "<!-- ================================================================== -->"
        echo "<!-- $title -->"
        echo "<!-- ================================================================== -->"
        echo "$content"
    } >> "$OUTPUT_FILE"
}

# ==============================================================================
# メインの収集処理
# ==============================================================================

# --- ヘッダー書き込み ---
DISPLAY_IP="$AVR_IP"
[[ "$MASK" == true ]] && DISPLAY_IP="XXX.XXX.XXX.XXX"

cat > "$OUTPUT_FILE" <<HEADER
<?xml version="1.0" encoding="utf-8"?>
<!--
  DENON AVC-A110 API サンプル
  サンプル名: ${SAMPLE_NAME}
  取得日時:   ${TIMESTAMP_HUMAN}
  AVR IP:     ${DISPLAY_IP}
  マスク:     ${MASK}
-->
<samples name="${SAMPLE_NAME}" timestamp="${TIMESTAMP_HUMAN}" avr="${DISPLAY_IP}">
HEADER

# ==============================================================================
# Batch 1: AppCommand.xml (シンプル形式)
# ==============================================================================
echo "=== Batch 1: AppCommand.xml ==="

BATCH1_BODY='<?xml version="1.0" encoding="utf-8"?>
<tx>
<cmd id="1">GetSurroundModeStatus</cmd>
<cmd id="2">GetAllZoneSource</cmd>
<cmd id="3">GetToneControl</cmd>
<cmd id="4">GetSubwooferLevel</cmd>
</tx>'

echo "  送信中: GetSurroundModeStatus, GetAllZoneSource, GetToneControl, GetSubwooferLevel"
BATCH1_RESP=$(post_xml "http://${AVR_IP}:${PORT}${APPCOMMAND_PATH}" "$BATCH1_BODY")

if [[ -n "$BATCH1_RESP" ]]; then
    BATCH1_RESP=$(apply_mask "$BATCH1_RESP")
    write_section "Batch 1: AppCommand.xml — GetSurroundModeStatus, GetAllZoneSource, GetToneControl, GetSubwooferLevel" "$BATCH1_RESP"
    ok "Batch 1 完了"
else
    fail "Batch 1 レスポンスが空です"
    write_section "Batch 1: AppCommand.xml" "<!-- 空レスポンス -->"
fi
echo ""

# ==============================================================================
# Batch 2: AppCommand0300.xml (パラメータ形式)
# 1リクエスト1コマンドで送信する (確実にデータを取得するため)
# ==============================================================================
echo "=== Batch 2: AppCommand0300.xml ==="

# コマンド定義: "コマンド名|param1,param2,..."
BATCH2_COMMANDS=(
    "GetAudioInfo|inputmode,output,signal,sound,fs"
    "GetVideoInfo|videooutput,hdmisigin,hdmisigout"
    "GetInputSignal|inputsigall"
    "GetActiveSpeaker|activespall"
    "GetSoundMode|movie,music,game,pure"
    "GetSoundModeList|genrelist"
    "GetSurroundParameter|centerimage,dimension,centerwidth,panorama"
    "GetAudyssey|dynamiceq,reflevoffset,dynamicvol,multeq"
    "GetAudyssyInfo|dynamiceq,dynamicvol"
    "GetRestorerMode|mode"
    "GetAudioDelay|audiodelay"
    "GetBassSync|basssync"
    "GetDynCompList|dyncompall"
    "GetDialogEnhancer|dialogenhancer"
    "GetIMAXList|imaxall"
)

CMD_INDEX=0
for entry in "${BATCH2_COMMANDS[@]}"; do
    CMD_INDEX=$((CMD_INDEX + 1))
    CMD_NAME="${entry%%|*}"
    PARAMS_CSV="${entry##*|}"

    # パラメータ行を組み立てる
    PARAM_LINES=""
    IFS=',' read -ra PARAM_ARRAY <<< "$PARAMS_CSV"
    for p in "${PARAM_ARRAY[@]}"; do
        PARAM_LINES="${PARAM_LINES}
<param name=\"${p}\" />"
    done

    # リクエスト XML を組み立てる (改行必須)
    REQ_BODY="<?xml version=\"1.0\" encoding=\"utf-8\"?>
<tx>
<cmd id=\"1\">
<name>${CMD_NAME}</name>
<list>${PARAM_LINES}
</list>
</cmd>
</tx>"

    echo "  [${CMD_INDEX}/15] ${CMD_NAME}..."
    RESP=$(post_xml "http://${AVR_IP}:${PORT}${APPCOMMAND0300_PATH}" "$REQ_BODY")

    if [[ -n "$RESP" ]]; then
        RESP=$(apply_mask "$RESP")
        write_section "Batch 2-${CMD_INDEX}: ${CMD_NAME}" "$RESP"
    else
        warn "${CMD_NAME}: レスポンスが空です"
        write_section "Batch 2-${CMD_INDEX}: ${CMD_NAME}" "<!-- 空レスポンス -->"
    fi
done

ok "Batch 2 完了 (${CMD_INDEX} コマンド)"
echo ""

# ==============================================================================
# サマリー生成
# ==============================================================================
echo "=== サマリー生成中 ==="

# ファイル全体を読み込んでサマリーを抽出
FILE_CONTENT=$(cat "$OUTPUT_FILE")

# macOS 互換の値抽出ヘルパー (BSD grep には -P がないため sed を使用)
extract_param() {
    local param_name="$1"
    local result
    result=$(echo "$FILE_CONTENT" | sed -n "s/.*<param name=\"${param_name}\"[^>]*>\([^<]*\)<.*/\1/p" | head -1)
    echo "${result:-N/A}"
}

# --- 信号フォーマット (GetAudioInfo の signal) ---
SIGNAL_FORMAT=$(extract_param "signal")

# --- サウンドモード (GetAudioInfo の sound) ---
SOUND_MODE=$(extract_param "sound")

# --- ソース入力 (GetAllZoneSource の source) ---
SOURCE_INPUT=$(echo "$FILE_CONTENT" | sed -n 's/.*<source>\([^<]*\)<.*/\1/p' | head -1)
SOURCE_INPUT="${SOURCE_INPUT:-N/A}"

# --- ビデオ信号 入力/出力 (GetVideoInfo) ---
VIDEO_IN=$(extract_param "hdmisigin")
VIDEO_OUT=$(extract_param "hdmisigout")

# --- アクティブスピーカー数 (GetActiveSpeaker セクション内の control="1" or "2") ---
ACTIVE_SPEAKERS=$(echo "$FILE_CONTENT" | sed -n '/GetActiveSpeaker/,/<!-- ===/p' | grep -c 'activesp.*control="[12]"' 2>/dev/null || echo "0")

# --- Audyssey MultEQ ---
MULTEQ_STATUS=$(extract_param "multeq")

# --- サマリーをファイルに書き込み ---
{
    echo ""
    echo "<!-- ================================================================== -->"
    echo "<!-- サマリー -->"
    echo "<!-- ================================================================== -->"
    echo "<!--"
    echo "  信号フォーマット:      ${SIGNAL_FORMAT}"
    echo "  サウンドモード:        ${SOUND_MODE}"
    echo "  ソース入力:            ${SOURCE_INPUT}"
    echo "  ビデオ信号 (入力):     ${VIDEO_IN}"
    echo "  ビデオ信号 (出力):     ${VIDEO_OUT}"
    echo "  アクティブスピーカー数: ${ACTIVE_SPEAKERS}"
    echo "  Audyssey MultEQ:       ${MULTEQ_STATUS}"
    echo "-->"
    echo ""
    echo "</samples>"
} >> "$OUTPUT_FILE"

# --- サマリーをコンソールにも表示 ---
echo ""
echo "=============================="
echo " サマリー"
echo "=============================="
echo "  信号フォーマット:      ${SIGNAL_FORMAT}"
echo "  サウンドモード:        ${SOUND_MODE}"
echo "  ソース入力:            ${SOURCE_INPUT}"
echo "  ビデオ信号 (入力):     ${VIDEO_IN}"
echo "  ビデオ信号 (出力):     ${VIDEO_OUT}"
echo "  アクティブスピーカー数: ${ACTIVE_SPEAKERS}"
echo "  Audyssey MultEQ:       ${MULTEQ_STATUS}"
echo "=============================="
echo ""
ok "サンプル保存完了: ${OUTPUT_FILE}"
