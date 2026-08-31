#!/usr/bin/env bash
# verify.sh — print media spec for an mp4 and build a 4x4 contact sheet PNG.
# Usage: verify.sh <path-to-mp4>

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <mp4>" >&2
  exit 1
fi

IN="$1"
# verify.sh lives at brand/video/scripts/verify.sh; parent of parent is brand/video.
BV="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$BV/work"
CLIPS="$WORK/clips"
SHEET="$CLIPS/contact_sheet.png"
mkdir -p "$CLIPS"

echo "==> ffprobe spec for: $IN"
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,codec_long_name,profile,width,height,avg_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 "$IN"

echo "==> streams (audio present?)"
ffprobe -v error -show_entries stream=codec_type \
  -of compact=p=0:nk=1 "$IN" | sort | uniq -c

echo "==> duration"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$IN"

echo "==> building 4x4 contact sheet -> $SHEET"
ffmpeg -y -i "$IN" -vf "fps=1/2,tile=4x4" -frames:v 1 "$SHEET" -loglevel error
ls -l "$SHEET"
