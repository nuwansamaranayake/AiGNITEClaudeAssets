# Quantum Entanglement film: full rebuild on Windows (PowerShell 7+).
# Resume safe: finished Blender frames are skipped, so you can stop and re-run at any time.
# Requirements: Python 3.11 (bpy 4.5 needs exactly 3.11), Node.js 18+, about 25 GB free disk.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 1. Python environment
if (-not (Test-Path .venv)) { py -3.11 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install --quiet bpy==4.5.3 edge-tts "numpy<2.0,>=1.26" "opencv-python-headless<4.11" "scipy<1.14" pyloudnorm soundfile imageio-ffmpeg
$py = ".\.venv\Scripts\python.exe"

# 2. Source imagery (NASA Visible Earth is public domain, Poly Haven is CC0)
New-Item -ItemType Directory -Force tex, audio, clips, plates, tracks, logs | Out-Null
$downloads = @{
  "tex\earth_day.jpg"      = "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74218/world.200412.3x5400x2700.jpg"
  "tex\earth_clouds.jpg"   = "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57747/cloud_combined_2048.jpg"
  "tex\earth_night.jpg"    = "https://eoimages.gsfc.nasa.gov/images/imagerecords/144000/144898/BlackMarble_2016_01deg.jpg"
  "tex\earth_night_hi.jpg" = "https://eoimages.gsfc.nasa.gov/images/imagerecords/144000/144898/BlackMarble_2016_3km.jpg"
  "tex\studio.hdr"         = "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/studio_small_09_2k.hdr"
}
foreach ($k in $downloads.Keys) { if (-not (Test-Path $k)) { Invoke-WebRequest $downloads[$k] -OutFile $k } }

# 3. Voice, timing, events, captions
& $py scripts\generate_tts.py
& $py scripts\compute_timeline.py
& $py scripts\make_events.py
& $py scripts\make_captions.py

# 4. Procedural textures
if (-not (Test-Path tex\sky.exr))    { & $py scripts\make_starfield.py tex\sky.exr 12288 }
if (-not (Test-Path tex\galaxy.exr)) { & $py scripts\make_galaxy.py tex\galaxy.exr 4096 }
& $py scripts\make_ocean_mask.py

# 5. Render and finish every 3D shot (Cycles on CPU, then bloom, lens, grade and grain)
$postArgs = Get-Content post_args.json | ConvertFrom-Json
$shots = "s01_birth","s02_pair","s03a","s03b","s03c","s04a","s04b","spr_undecided","spr_blue","spr_gold","s06_boxes","s08_real","s09_outro"
foreach ($sid in $shots) {
  & $py "blender\shot_$sid.py" | Tee-Object "logs\$sid.log" | Select-String "RENDERED|DONE|Error"
  $extra = @(); if ($postArgs.$sid) { $extra = $postArgs.$sid -split " " }
  & $py scripts\post.py "renders\$sid" "clips\$sid.mp4" @extra
}

# 6. Plates and screen tracks for the overlays
& $py blender\plates.py s04a
& $py blender\plates.py s04b
$env:QE_PLATE = "1"; & $py blender\shot_s03c.py; Remove-Item Env:\QE_PLATE
foreach ($f in "s04a_plate","s04b_plate","galaxy_plate") { & $py scripts\post.py plates "plates\${f}_post.png" --still "$f.png" --grain 0 }
$tracks = @{ "s02_pair"="A,B"; "s03a"="A,B"; "s03b"="A,B"; "s03c"="A,B"; "s06_boxes"="BoxLc,BoxRc"; "s08_real"="Sat,marker0,marker1"; "s09_outro"="A,B" }
foreach ($k in $tracks.Keys) { $env:QE_TRACK = $tracks[$k]; & $py "blender\shot_$k.py"; Remove-Item Env:\QE_TRACK }

# 7. Soundtrack (voice + original score + sound design, -16 LUFS)
& $py scripts\make_audio.py

# 8. Assemble with Remotion
Set-Location remotion
Copy-Item ..\events.json, ..\timeline.json, ..\captions.json src\data\ -Force
Copy-Item ..\tracks\*.json, ..\plates\*.json src\data\ -Force
New-Item -ItemType Directory -Force public\plates, public\audio, public\fonts | Out-Null
Copy-Item ..\plates\*_post.png public\plates\ -Force
Copy-Item ..\audio\soundtrack.wav public\audio\ -Force
if (-not (Test-Path public\clips)) { New-Item -ItemType Junction -Path public\clips -Target (Resolve-Path ..\clips) | Out-Null }
npm install --no-audit --no-fund
Copy-Item node_modules\@fontsource\inter\files\inter-latin-*-normal.woff2 public\fonts\ -Force
npx remotion render src/index.ts Film out/quantum-entanglement.mp4 --codec h264 --crf 17 --audio-codec aac --audio-bitrate 320k
Write-Host "Done: remotion\out\quantum-entanglement.mp4"
