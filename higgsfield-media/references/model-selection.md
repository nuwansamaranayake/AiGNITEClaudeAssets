# Model Selection

One-line summary: How to pick the right Higgsfield model for a given brief, with the full decision matrix and three worked examples.

## The matrix

### Image briefs

| Brief attribute | Primary model | Fallback | Reason |
|-----------------|---------------|----------|--------|
| Text on packaging, signage, labels | Nano Banana Pro | Nano Banana 2 | 4K text rendering, ~2 credits, paid |
| Editorial portrait, fashion shoot | Soul V2 | Cinema Studio | Free pool on Plus, magazine-grade |
| Sri Lankan e-commerce product on a person | Soul V2 | GPT Image 2 | Free pool, editorial style fits saree and apparel |
| Photorealism, product plus human | GPT Image 2 | Soul V2 | Unlimited on Plus, strong likeness |
| Stylized illustration, blog hero | Flux 2 Pro | Seedream 5.0 Lite | Unlimited on Plus, faithful to brief |
| Concept diagram, abstract idea | Seedream 5.0 Lite | Flux 2 Pro | Visual reasoning, unlimited |
| Architecture diagram backdrop | Seedream 4.5 | Flux 2 Pro | High resolution, unlimited |
| Quick variant batch for prompt testing | Nano Banana 2 (2K) | Flux 2 Pro | Unlimited, fast |
| Storyboard frame | Kling O1 Image | Soul V2 | Reasoning tier, unlimited |
| Cinematic still photography | Cinema Studio | Soul V2 | Free pool, Marketing Studio quality |

### Video briefs

| Brief attribute | Primary model | Fallback | Reason |
|-----------------|---------------|----------|--------|
| 5-second product motion clip | Seedance 2.0 | Kling 3.0 | Audio-video sync, ~9 credits |
| Polished 4K social cut, 5-10 sec | Kling 3.0 | Wan 2.6 | Camera control, ~6 credits |
| UGC talking head with lip-sync | Seedance 2.0 | Lipsync Studio post-pass | Single-pass audio |
| 8-second narrative beat | Veo 3.1 | Kling 3.0 | Long-form coherence, 40 to 70 credits |
| 15-second cinematic ad with physics | Sora 2 | Veo 3.1 | Object permanence, 40 to 70 credits |
| Cinematic motion video, free pool | Soul Cinema | Cinema Studio | 5,000 free generations |
| Variant batch for prompt testing | Wan 2.6 | Kling 2.5 Turbo | Budget tier, fast |
| Character animation, stylized | Hailuo 02 | Kling 2.6 | Character motion specialist |

## Choosing between unlimited models

When two unlimited models could both serve the brief, pick:

- Flux 2 Pro for stylized illustration, blog hero, AEO content
- GPT Image 2 for photorealism, especially involving people
- Seedream 4.5 for high-resolution stills, architectural detail
- Seedream 5.0 Lite for concept-heavy or abstract prompts
- Kling O1 Image for storyboard frames where reasoning matters

## Worked example 1: LinkedIn cover for AiGNITE

Brief: "Generate a LinkedIn cover at 1128x191 with the AiGNITE green and red yin-yang motif, dark background, premium technology feel."

Walk:

- Asset type: image
- Aspect ratio: 1128x191 (extreme banner)
- Subject: brand mark
- Style: dark background, premium technology
- Text requirement: optional (brand name)
- Quantity: typically 3 variations

Decision: Nano Banana Pro. The brand mark has text-like geometry and the brief implies polished render. Cost: 6 credits for 3 images.

Confirmation: under 100 credits total, proceed without asking.

## Worked example 2: FloodPulse product motion clip

Brief: "5-second clip for FloodPulse showing the dashboard flood-risk map fading into a Houston aerial."

Walk:

- Asset type: video
- Duration: 5 seconds
- Aspect ratio: 16:9
- Subject: dashboard plus aerial
- Style: smooth transition, motion graphic feel
- Text requirement: dashboard text legibility helpful but not critical
- Quantity: single clip

Decision: Seedance 2.0. Audio-video sync in one pass is a tiebreaker even if no audio is needed because the model handles motion blending cleanly. Cost: ~9 credits.

Confirmation: under 40 credits, proceed without asking.

## Worked example 3: 15-second Cosmic Nexus ad with physics

Brief: "15-second cinematic ad for Cosmic Nexus where birth-chart wheels spin in the air, glass shatters revealing a Vedic mandala. Native audio."

Walk:

- Asset type: video
- Duration: 15 seconds
- Aspect ratio: 9:16 (Reels) or 16:9
- Subject: animated chart wheels and breaking glass
- Style: cinematic with physics
- Text requirement: brand name on closing frame
- Quantity: single hero clip

Decision: Sora 2. Object permanence and physics over 15 seconds is the model's lane. Cost: ~60 credits. Confirmation: over 40 credits per generation, ask the user explicitly before submitting.

## Cost-aware variants

When the user has a tight budget:

- Iterate on prompts with Wan 2.6 (low) or Kling 2.5 Turbo (low) until satisfied
- Run the final pass on Kling 3.0, Seedance 2.0, Veo 3.1, or Sora 2 only

Never burn premium credits on first-draft prompt validation.

## When to use Marketing Studio presets

The Marketing Studio presets are canned modes (UGC, unboxing, product review, TV spot, hyper motion, hero banner, Pinterest pin, ad pack, lifestyle, flat lay). Pick a preset over a raw model when the brief matches the preset's purpose exactly. See [marketing-studio-presets.md](marketing-studio-presets.md).

## When to use Soul Character

Reach for Soul Character when the brief needs the same person across more than two shots. The cost is one training pass plus per-shot generation. Cheaper than re-prompting for likeness on every frame. See [soul-character-workflow.md](soul-character-workflow.md).
