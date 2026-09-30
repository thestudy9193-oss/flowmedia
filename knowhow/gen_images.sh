#!/usr/bin/env bash
# 노하우 대표 이미지 생성 (codex-image gen.sh 경유). 사용: bash knowhow/gen_images.sh [slug...]
D="$(cd "$(dirname "$0")" && pwd)/images"; G=~/.claude/skills/codex-image/scripts/gen.sh
STYLE='Editorial photograph for a Korean video production agency blog, 16:9, cinematic moody lighting, dark near-black tones with subtle neon lime green (#beff0f) accent light, shallow depth of field, realistic, premium. ABSOLUTELY NO text, letters, numbers, captions, subtitles, watermarks or brand logos anywhere in the image (screens show only abstract imagery).'
prompt_for() {
  case "$1" in
    shortform-first-3-seconds) echo "close-up of a thumb about to scroll a vertical smartphone video feed, the video on screen is a dramatic freeze-frame moment";;
    reels-editing-rhythm) echo "video editor's hands on a keyboard and jog wheel, monitor showing a colorful timeline with many short clips aligned to an audio waveform";;
    shortform-lighting-setup) echo "smartphone on a small tripod filming a person by a window, a compact LED panel and a reflector creating soft light";;
    shorts-length-structure) echo "vertical smartphone showing a looping video, a glowing circular loop light trail around the phone on a dark desk";;
    shortform-script-structure) echo "a notebook with a hand-drawn three-part storyboard sketch (only drawings, no words), pen and smartphone on a dark desk";;
    professional-shortform-filming) echo "a professional in a suit speaking to a cinema camera in a clean modern office studio with softbox lights, trustworthy mood";;
    longform-to-shorts) echo "an editing monitor showing one widescreen video frame being split into several vertical frames, editor silhouette";;
    reels-subtitle-design) echo "vertical phone screen showing a lifestyle video with large bold abstract subtitle bars (blank shapes, no letters), designer's desk";;
    shortform-audio-tips) echo "a lavalier microphone clipped on a shirt and a shotgun mic on a camera, recording on location, audio levels glowing";;
    youtube-thumbnail-title) echo "a designer's monitor showing a grid of blank colorful video thumbnail frames with expressive faces, no text";;
    store-reels-batch-shooting) echo "a filmmaker with a gimbal shooting inside a cozy Korean restaurant, sizzling grilled beef on the table";;
    choosing-shortform-agency) echo "a business meeting table with a laptop showing a video portfolio grid, two people discussing, coffee cups";;
    shorts-upload-checklist) echo "a smartphone showing an upload progress screen (abstract, no text) next to a checklist notepad with tick marks only";;
    shortform-moodboard) echo "a physical moodboard wall with printed photos, color swatches and fabric samples, lime accent, creative studio";;
    shortform-analytics-metrics) echo "a laptop screen with abstract glowing analytics charts and graphs (no numbers), dark office";;
    reels-trending-audio) echo "headphones and a smartphone showing a vertical video with a pulsing audio waveform, music vibe";;
    shorts-series-planning) echo "a wall of sticky-note cards arranged in a sequence of episode columns (blank notes), planning session";;
    youtube-channel-first-month) echo "a desk calendar grid with a few days marked by lime stickers, a camera and laptop beside it, planning mood";;
    shortform-camera-angles) echo "a camera operator shooting from a low angle with a gimbal, multiple angle frames implied by lights, dynamic composition";;
    shortform-cta-conversion) echo "a smartphone showing a vertical video with a glowing tap button shape (no text) and a hand reaching to tap it";;
  esac
}
ALL="shortform-first-3-seconds reels-editing-rhythm shortform-lighting-setup shorts-length-structure shortform-script-structure professional-shortform-filming longform-to-shorts reels-subtitle-design shortform-audio-tips youtube-thumbnail-title store-reels-batch-shooting choosing-shortform-agency shorts-upload-checklist shortform-moodboard shortform-analytics-metrics reels-trending-audio shorts-series-planning youtube-channel-first-month shortform-camera-angles shortform-cta-conversion"
slugs=("$@"); [ ${#slugs[@]} -eq 0 ] && slugs=($ALL)
i=0
for s in "${slugs[@]}"; do
  [ -f "$D/$s.jpg" ] && continue
  ( bash "$G" --prompt "$STYLE Scene: $(prompt_for "$s")" --out "$D/$s.png" --orientation landscape --width 1280 --height 720 </dev/null >"$D/$s.log" 2>&1 \
    && sips -s format jpeg -s formatOptions 82 "$D/$s.png" --out "$D/$s.jpg" >/dev/null && rm -f "$D/$s.png" "$D/$s.log"; echo "done $s" ) &
  i=$((i+1)); if [ $((i%5)) -eq 0 ]; then wait; fi
done
wait; ls "$D"
