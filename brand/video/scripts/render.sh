#!/usr/bin/env bash
# render.sh — Ken Burns still edit + xfade assembly -> picture_only.mp4 (~60s, 1920x1080@30).
# Re-runnable from any cwd: resolves brand/video via the git worktree root.

set -euo pipefail

# --- Resolve brand/video root relative to this script (cwd-independent) ---
# render.sh lives at brand/video/scripts/render.sh, so its parent's parent is brand/video.
BV="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$BV/work"
CLIPS="$WORK/clips"
TMP="$CLIPS/tmp"
OUT="$CLIPS/picture_only.mp4"
mkdir -p "$TMP"

FADE=0.4            # xfade duration (seconds)
TARGET=60           # target net duration (seconds)
FPS=30              # all sources share this frame rate

# --- Shot list: TYPE | ASSET | DIRECTION | BASE_DUR ---
# TYPE: clip (trim mp4 as-is) | still (Ken Burns on png)
shots=(
  "clip  work/ai/intro.mp4          as-is     3.2"
  "still work/frames/welcome.png     zoom-in   4.0"
  "still work/screens/login.png      pan-left  3.0"
  "still work/screens/dashboard.png  zoom-in   3.4"
  "still work/screens/dashboard.png  pan-right 2.6"
  "still work/screens/wizard-job.png zoom-in   3.0"
  "still work/screens/wizard-role.png pan-left 3.0"
  "still work/screens/wizard-review.png zoom-in 3.4"
  "still work/frames/section-discover.png zoom-out 2.0"
  "still work/screens/catalog.png    pan-right 2.4"
  "still work/screens/catalog-category.png zoom-in 2.4"
  "still work/screens/catalog-skill.png pan-left 2.4"
  "still work/screens/learn.png      zoom-in   3.2"
  "still work/screens/analytics.png  zoom-out  3.4"
  "still work/frames/section-admin.png zoom-in 2.0"
  "still work/screens/admin-dashboard.png pan-left 2.6"
  "still work/screens/admin-users.png zoom-in   2.4"
  "still work/screens/admin-reports.png pan-right 2.4"
  "still work/frames/close.png       zoom-in   3.6"
  "clip  work/ai/outro.mp4           as-is     5.0"
)

n=${#shots[@]}

# --- Duration scaling ---
# Only still durations (index 2-19) are scaled by one uniform factor so that
# net = sum(dur) - (n-1)*FADE lands on TARGET. Intro/outro clips are fixed.
still_sum=0
for ((i=0; i<n; i++)); do
  read -r typ asset dir dur <<<"${shots[$i]}"
  if [[ "$typ" == "still" ]]; then
    still_sum=$(awk -v s="$still_sum" -v d="$dur" 'BEGIN{print s+d}')
  fi
done

# net(dur_with_factor) = (clips + still_sum*factor) - (n-1)*FADE = TARGET
# => factor = (TARGET + (n-1)*FADE - clips) / still_sum
clips_sum=$(awk 'BEGIN{s=0} {if($1=="clip") s+=$4} END{print s}' <<<"$(for s in "${shots[@]}"; do echo "$s"; done)")
factor=$(awk -v t="$TARGET" -v fade="$FADE" -v n="$n" -v cs="$clips_sum" -v ss="$still_sum" \
  'BEGIN{print (t + (n-1)*fade - cs) / ss}')

durs=()          # final duration per shot
for ((i=0; i<n; i++)); do
  read -r typ asset dir dur <<<"${shots[$i]}"
  if [[ "$typ" == "still" ]]; then
    dur=$(awk -v d="$dur" -v f="$factor" 'BEGIN{printf "%.4f", d*f}')
  fi
  durs+=("$dur")
done

echo "==> duration factor = $factor  (still durations scaled uniformly)"
echo "==> net target = ${TARGET}s"

# --- Ken Burns direction expressions (smooth, jitter-free) ---
# zoompan has no `f` option; inline the fraction f=on/(D*FPS-1) into each expr.
kb_expr() {
  local dir="$1" fps="$2" dur="$3"
  local fr
  fr=$(awk -v d="$dur" -v fps="$fps" 'BEGIN{printf "on/(%.4f*%d-1)", d, fps}')
  case "$dir" in
    zoom-in)  echo "z=1.0+0.20*($fr):x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)" ;;
    zoom-out) echo "z=1.20-0.20*($fr):x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)" ;;
    pan-left) echo "z=1.20:x=(iw-iw/zoom)*(1-($fr)):y=(ih-ih/zoom)/2" ;;
    pan-right) echo "z=1.20:x=(iw-iw/zoom)*($fr):y=(ih-ih/zoom)/2" ;;
    *) echo "z=1.0+0.20*($fr):x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)" ;;
  esac
}

# --- Render each shot to a per-shot clip ---
seg_files=()
for ((i=0; i<n; i++)); do
  read -r typ asset dir _dur <<<"${shots[$i]}"
  dur="${durs[$i]}"          # use the (possibly scaled) final duration
  seg="$TMP/seg_$(printf '%02d' "$i").mp4"
  seg_files+=("$seg")
  echo "==> rendering shot $(printf '%02d' "$i"): $typ $asset ($dur s)"
  if [[ "$typ" == "clip" ]]; then
    # intro/outro: trim to exact duration, preserve 1920x1080@30, no audio
    ffmpeg -y -ss 0 -t "$dur" -i "$BV/$asset" -an \
      -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -r "$FPS" "$seg" \
      -loglevel error
  else
    expr="$(kb_expr "$dir" "$FPS" "$dur")"
    ffmpeg -y -loop 1 -framerate "$FPS" -t "$dur" -i "$BV/$asset" -an \
      -filter_complex "scale=3840:2160,zoompan=d=1:s=1920x1080:fps=$FPS:$expr" \
      -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p "$seg" \
      -loglevel error
  fi
done

# --- xfade chain: offset_k = (sum durs 1..k) - k*FADE ---
filter=""
prev="0"
acc=0
for ((k=0; k<n-1; k++)); do
  acc=$(awk -v a="$acc" -v d="${durs[$k]}" 'BEGIN{print a+d}')
  off=$(awk -v a="$acc" -v k="$((k+1))" -v fade="$FADE" 'BEGIN{printf "%.4f", a - k*fade}')
  out="v$((k+1))"
  if [[ -z "$filter" ]]; then
    filter="[0][1]xfade=transition=fade:duration=$FADE:offset=$off[$out]"
  else
    prev_out="${prev}"
    filter="$filter;[$prev_out][$((k+1))]xfade=transition=fade:duration=$FADE:offset=$off[$out]"
  fi
  prev="$out"
done

inputs=()
for f in "${seg_files[@]}"; do inputs+=(-i "$f"); done

echo "==> xfade-assembling ${#seg_files[@]} shots -> $OUT"
ffmpeg -y "${inputs[@]}" \
  -filter_complex "$filter" \
  -map "[$prev]" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUT" -loglevel error

echo "==> done: $OUT"
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,pix_fmt \
  -show_entries format=duration -of default=noprint_wrappers=1 "$OUT"
