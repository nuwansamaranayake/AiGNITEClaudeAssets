# Prompting Cookbook

One-line summary: Model-specific prompt templates with annotated parts. Each model has a personality. Match the prompt to the model.

## Universal template parts

Every Higgsfield prompt benefits from these six parts. Different models weight them differently.

1. Subject: who or what is in the frame
2. Action: what is happening
3. Camera: lens, angle, distance
4. Lighting: source, quality, mood
5. Style: realism, illustration, editorial, cinematic
6. Technical: aspect ratio, resolution hint, negative prompt

## Nano Banana Pro

Personality: best 4K text rendering on packaging, signage, labels. Likes concrete spatial cues.

Template:

```
Subject: <product> with <text on label or sign>
Camera: <angle>, <distance>, <lens>
Lighting: <source>, <quality>
Style: <realism level>, <color palette>
Composition: <text placement>, <focal point>
Resolution: 4K
```

Example for AiGNITE LinkedIn cover:

```
Subject: AiGNITE Consulting logo in green and red yin-yang motif
Camera: straight-on, banner crop 1128x191, wide-angle feel
Lighting: low-key studio with rim light from the right
Style: premium technology branding, dark navy background
Composition: logo centered, generous negative space, no caption text
Resolution: 4K
Negative prompt: cluttered background, gradient noise, photo grain
```

Tips:

- Be explicit about which text must render. The model can render legible copy when told what to render.
- Avoid asking for multiple copy blocks in the same image.
- Specify the aspect ratio in the prompt as well as in the parameter.

## Soul V2

Personality: editorial portraits, fashion, lifestyle. Likes magazine vocabulary.

Template:

```
Subject: <demographic>, <wardrobe>, <mood>
Setting: <location>, <time of day>
Camera: <medium close-up | full body>, <85mm | 35mm>
Lighting: <golden hour | softbox | window light>
Style: editorial fashion photography, <Vogue Italia | Kinfolk | National Geographic>
Aspect ratio: 4:5
```

Example for DrapeStudio:

```
Subject: thirty-year-old Sri Lankan woman in a deep green silk saree with gold border
Setting: Galle Fort sandstone wall at golden hour
Camera: medium close-up, 85mm prime, shallow depth of field
Lighting: warm side light, soft shadow on the wall behind her
Style: editorial fashion photography, Vogue India aesthetic
Aspect ratio: 4:5
Negative prompt: oversaturated, plastic skin, generic stock photo feel
```

Tips:

- Soul V2 responds well to a named editorial reference (Vogue Italia, Kinfolk, etc.).
- Specifying a demonym (Sri Lankan, Houstonian, Mumbai) returns better-fitting faces.
- Avoid Western-default fashion vocabulary when the brief is South Asian.

## GPT Image 2

Personality: photorealism with people, complex compositions. Likes natural language.

Template:

```
A <scene description> showing <person> <action> <object>. The setting is <environment>.
The lighting is <quality>. The camera is <position and lens>. The mood is <feeling>.
```

Example for FloodPulse marketing:

```
A wide-angle shot of a Houston resident pointing at a tablet displaying a flood risk map.
The setting is their kitchen table during a rainy afternoon. The lighting is warm overhead with
diffused window light from the left. The camera is at eye level, 35mm prime, focused on the tablet
with the resident's hand and face slightly soft. The mood is calm reassurance.
```

Tips:

- Use sentence-form prose, not bullet lists.
- Name the camera position and focal length to control compression.
- Use mood as the closing line, not as an opening adjective.

## Flux 2 Pro

Personality: stylized illustration, fast and faithful. Likes style + subject combos.

Template:

```
<style descriptor>, <subject>, <key visual element>, <color palette>, <composition>
```

Example for AEO insight page cover:

```
flat vector illustration, search engine results redesigned as a glowing knowledge graph,
nodes pulsing with citation count, palette of indigo and emerald, isometric composition,
generous whitespace
```

Tips:

- Lead with the style descriptor. Flux 2 Pro weights the first phrase heavily.
- Three style adjectives is plenty; more confuses the output.
- For consistent series, reuse the style block verbatim across prompts.

## Seedream 5.0 Lite

Personality: visual reasoning, concept-heavy prompts. Handles abstract briefs well.

Template:

```
Concept: <abstract idea>
Visual metaphor: <concrete representation>
Style: <realism | illustration | diagrammatic>
```

Example for an AEO page about query intent:

```
Concept: user search intent splitting across multiple AI engines
Visual metaphor: a single beam of light entering a prism, splitting into colored beams labeled with engine names
Style: editorial illustration, gradient mesh, soft glow
```

Tips:

- The model needs the abstract concept stated, not just a description.
- Naming the visual metaphor unlocks reasoning-grade composition.

## Seedream 4.5

Personality: high-resolution stills, architectural detail. Likes precision.

Template:

```
<subject> in <setting>, <key architectural detail>, <lighting>, <camera>, ultra-high resolution
```

Example for an architecture diagram backdrop:

```
A clean modern data center server rack lit by cool blue overhead light, dust-free polished concrete floor,
deep shadow gradient, no people, 35mm wide-angle, ultra-high resolution
```

Tips:

- Specify "no people" if the diagram needs an empty backdrop.
- Lighting precision matters more than other models.

## Kling 3.0

Personality: video, camera-language verbs. Likes shot grammar.

Template:

```
<subject> <action>. Camera: <move>. Duration: <seconds>. Style: <look>.
```

Example for FloodPulse social cut:

```
Houston neighborhood aerial transforms into a flood risk dashboard overlay. Camera: slow push-in from above,
then tilt down to dashboard close-up. Duration: 5 seconds. Style: smooth cinematic, atmospheric.
```

Tips:

- Use camera-move verbs (push, pull, pan, tilt, dolly, crane).
- One scene per prompt. Multi-scene briefs go to Veo 3.1 or Sora 2.

## Seedance 2.0

Personality: audio-video sync, UGC. Likes a sentence-level script plus mood.

Template:

```
<character> says: "<line>". The setting is <where>. Mood: <feeling>. Camera: <type>.
```

Example for Cosmic Nexus UGC:

```
A thirty-five-year-old woman with warm features says: "I checked my Vedic chart this morning and the
career section actually matched what happened today at work." The setting is a sunlit home office.
Mood: genuine surprise. Camera: handheld smartphone feel, three-quarter angle.
```

Tips:

- Quote the line verbatim.
- Keep the line under 12 seconds of spoken content for a 5-second clip.
- Mood + camera at the end tunes the delivery.

## Veo 3.1

Personality: long narrative beats. Likes shot-list grammar.

Template:

```
Shot 1: <description>. Shot 2: <description>. Shot 3: <description>. Audio: <treatment>.
```

Example for Cosmic Nexus 8-second beat:

```
Shot 1: a hand opens a brass-bound book at golden hour, soft dust motes catch the light.
Shot 2: pages turn rapidly revealing a Vedic chart, paper texture detail.
Shot 3: the chart rises off the page as a 3D mandala, slow rotation.
Audio: tabla rhythm building under a low drone.
```

Tips:

- One shot per sentence.
- End with the audio direction line.

## Sora 2

Personality: 15-second cinematic with physics. Likes physics-aware language.

Template:

```
A <subject> <verb with physical interaction>. <Camera direction>. <Environmental detail>.
The <object> <responds to physics how>.
```

Example for a Cosmic Nexus ad:

```
A glass bottle containing a swirling galaxy falls from a table, slow motion. The camera rises with it,
backing into a wide shot. The bottle shatters on the wood floor. The glass shards arc outward and the
galaxy inside reforms in midair as a Vedic mandala, then settles slowly onto the broken glass.
```

Tips:

- Name the physical interaction explicitly (falls, shatters, refracts, deforms).
- Slow motion cues help the model commit to physics resolution.

## Negative prompts

Most Higgsfield models accept a negative prompt block. Use it sparingly. Good negative prompts:

- "cluttered background"
- "plastic skin"
- "oversaturated"
- "watermark"
- "low resolution"
- "extra fingers"
- "deformed face"

Bad negative prompts: long lists of style words, contradicting the positive prompt, or vague terms like "ugly".
