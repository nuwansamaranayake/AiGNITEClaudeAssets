# Quantum Entanglement: a short film

A 130-second, 1080p24 narrated film that explains quantum entanglement to someone with no physics background. Every shot is path-traced 3D (Blender Cycles), finished with a film look, then assembled with narration, captions, labels, an original score and sound design in Remotion.

## What the viewer learns, shot by shot

| # | Shot | Idea on screen |
|---|------|----------------|
| 1 | Birth | Two particles are born together in one flash of light. |
| 2 | The pair | Each particle is a swirl of blue and gold: no color is decided yet. |
| 3 | Far apart | One meter, across the Earth, across the galaxy. The link stays. |
| 4 | Measurement | Split screen with synchronized clocks. A turns blue by chance; at the same instant B turns gold. Slow-motion replay. |
| 5 | Repeat | Ten new pairs. Each side's list looks random. Side by side, every pair is opposite. |
| 6 | Not hidden balls | X-ray boxes show fixed blue and gold balls. Entangled particles have no hidden answer (2022 Nobel Prize in Physics). |
| 7 | No faster-than-light messages | You cannot choose your result. The pattern appears only after comparing notes, which travel at light speed. |
| 8 | Real | Micius satellite (2017) sends entangled light to Delingha and Lijiang, 1,203 km apart. |
| 9 | Outro | Two particles, far apart, acting as one. |

## Pipeline

```
narration.json -> edge-tts voice + word timings -> timeline.json -> events.json
                                                    |               |
            Blender 4.5 Cycles (blender/*.py) <-----+               +--> make_audio.py (score, SFX, -16 LUFS)
                     |                                              +--> Remotion overlays and captions
            post.py (bloom, lens, grade, grain) -> clips/*.mp4 ------+--> Remotion render -> final MP4
```

Every animated value in Blender is computed from shot time inside a frame handler, so any frame renders on its own (resume safe) and the slow-motion replay is only a remap of time. All beats (flash, measurement, trial results, arrivals) come from the voice's word timings, so picture, sound effects and captions stay locked when the script changes.

## Rebuild on Windows

```powershell
cd showcase\quantum-entanglement-film
.\render.ps1
```

Needs Python 3.11 (bpy 4.5 requires it), Node.js 18+, and about 25 GB of free disk. On a 4-core CPU the full render takes roughly 6 hours. A GPU cuts that sharply: set `sc.cycles.device = "GPU"` in `blender/qe_lib.py`.

## Quality gates

`scripts/qa_video.py` checks 1920x1080, 24 fps, H.264 and AAC stereo, exact duration, -16 LUFS integrated loudness, true peak at or below -1 dBFS, no black gaps, and no frozen picture. `scripts/make_audio.py` also checks that narration sits at least 12 dB above music and effects while it speaks.

## Sources and licenses

- Physics facts: NobelPrize.org, Physics 2022 (Aspect, Clauser, Zeilinger). Yin et al., "Satellite-based entanglement distribution over 1200 kilometers", Science 356, 1140 (2017).
- Earth imagery: NASA Visible Earth (Blue Marble, Black Marble, clouds), public domain.
- Studio lighting: Poly Haven `studio_small_09`, CC0.
- Font: Inter, SIL Open Font License.
- Voice: Microsoft neural voice `en-US-AndrewMultilingualNeural` through the open-source `edge-tts` client. Check Microsoft's terms before commercial use, or switch to ElevenLabs as described in the remotion-video skill.
- Star field, galaxy, score and sound effects: generated procedurally by the scripts in this folder.
