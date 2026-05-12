# Marketing Studio Presets

One-line summary: The Higgsfield Marketing Studio canned modes, what each one does, and the brief shape that maps to each preset.

## What presets are

Marketing Studio is a set of pre-tuned prompts and model pipelines that produce specific commercial-grade outputs from a short brief. Pick a preset over a raw model when the brief matches the preset's purpose exactly. Presets bundle camera, lighting, and post-processing decisions so the operator skips those.

## The presets

### UGC

Output: user-generated-content-style talking head or hands-on demo, vertical 9:16.
Best for: Fiverr astrology clips, Instagram Reels with a spokesperson, TikTok product reviews.
Brief shape: "30-year-old woman holds the product, says 'I tried this last week and...', smartphone footage feel."
Underlying model: Seedance 2.0 with lip-sync.
Credits: ~9 per clip.

### Unboxing

Output: top-down or three-quarter angle product unboxing, 1:1 or 9:16.
Best for: e-commerce launches (DrapeStudio), gift product reveals.
Brief shape: "Two hands opening a kraft mailer, slow reveal of a folded saree, soft natural light."
Underlying model: Kling 3.0 or Seedance 2.0.
Credits: ~6 to 9.

### Product Review

Output: angled product shot with a face partially in frame reacting, 9:16.
Best for: ad-creative-style endorsements.
Brief shape: "User holds the bottle, turns it slowly, soft smile, white kitchen background."
Underlying model: Seedance 2.0.
Credits: ~9.

### TV Spot

Output: 15-second cinematic ad with multiple cuts, 16:9.
Best for: Cosmic Nexus promo, AiGNITE Consulting brand spot.
Brief shape: shot list with three to four scenes, ends on logo card.
Underlying model: Sora 2 or Veo 3.1.
Credits: 40 to 70.

### Hyper Motion

Output: fast-cut action sequence with motion blur, 16:9 or 9:16.
Best for: launch reels, energetic openers.
Brief shape: "Camera whip pans through the office, lights flicker, dashboard appears with rising number."
Underlying model: Kling 3.0.
Credits: ~6 to 12.

### Hero Banner

Output: cinematic still photography, 16:9 wide aspect.
Best for: web hero images, LinkedIn covers, newsletter mastheads.
Brief shape: single subject, dramatic lighting, atmospheric setting.
Underlying model: Cinema Studio.
Credits: free pool.

### Pinterest Pin

Output: 2:3 vertical, lifestyle composition with copy space.
Best for: AEO insight covers, blog hero variants for Pinterest pinning.
Brief shape: "Top-down flat lay of a planner and coffee on a marble desk, soft morning light."
Underlying model: Cinema Studio or Soul V2.
Credits: free pool.

### Ad Pack

Output: six asset bundle including a square hero, a 9:16 short clip, a 16:9 banner, two product stills, one lifestyle shot.
Best for: a full campaign launch in one brief.
Brief shape: "Build an ad pack for [product], emphasize [hero benefit], target [audience]."
Underlying models: mixed; the skill expands the preset into six model calls.
Credits: 30 to 80 depending on chosen tier.

### Lifestyle

Output: editorial portrait with environmental context, 4:5.
Best for: Sri Lankan e-commerce product worn by a model, food photography.
Brief shape: "Mid-thirties woman in a green saree on a Galle Fort balcony at golden hour."
Underlying model: Soul V2.
Credits: free pool.

### Flat Lay

Output: top-down arranged composition, 1:1.
Best for: product line shots, recipe components, gift sets.
Brief shape: "Top-down arrangement of brass lamps, marigolds, and an open notebook on dark wood."
Underlying model: Cinema Studio or Nano Banana Pro for text-on-label legibility.
Credits: free pool or ~2 if text matters.

## When not to use a preset

If the brief mixes two preset purposes (e.g. UGC plus product reveal), build a custom prompt against the underlying model directly. Presets are for narrow purposes, not blended ones.

If the brief calls for an unusual aspect ratio not in the preset's defaults, use the underlying model directly with explicit parameters.
