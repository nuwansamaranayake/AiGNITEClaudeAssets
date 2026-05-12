# Soul Character Workflow

One-line summary: Train a character once from reference photos, then reuse the character ID across many shots so likeness stays consistent without re-prompting.

## When to use Soul Character

Reach for Soul Character when the brief needs the same person across more than two shots. Examples:

- A four-clip UGC series with the same spokesperson
- A six-image lifestyle pack for an e-commerce product worn by one model
- A multi-screen walkthrough video where one face appears in every screen
- A storyboard of seven frames with a recurring protagonist

For one or two shots, prompting the model directly is faster.

## Training cost

One training pass per character. The pass takes 3-5 minutes and burns a small amount of credits (verify current cost in [credit-costs.md](credit-costs.md), typically under 10). After training, every per-shot generation against the character ID costs the standard per-model rate, no extra.

## Inputs for training

- 3 to 5 reference photos of the person
- Variety helps: different angles, lighting, expressions
- Plain background preferred but not required
- Minimum 1024x1024 each
- Same person in every photo

## Training step

The MCP tool name is typically `create_character` or `train_character`. Verify the exact tool name with `claude mcp get higgsfield` in a scratch directory.

Call shape:

```
create_character(
  name="cosmic-nexus-spokesperson",
  reference_images=[
    "path/to/ref1.jpg",
    "path/to/ref2.jpg",
    "path/to/ref3.jpg"
  ],
  notes="thirty-five years old, warm features, professional context"
)
```

Wait for the training job to return a character_id. Save the id to the project's `manifest.json` under a top-level `characters` map.

## Reusing in generation

Once trained, reference the character ID in any image or video prompt:

```
generate_video(
  model="seedance-2.0",
  character_id="char_abc123",
  prompt="The character says: '<line>'. Setting: sunlit home office. Mood: genuine."
)
```

The model uses the character ID to anchor likeness. The prompt drives action, setting, mood.

## Workflow for a UGC series

1. Pick the model (typically Seedance 2.0 with lip-sync for talking head).
2. Train the character.
3. Write the script in beats. One beat per clip.
4. Generate each clip with the same character_id, different prompts per beat.
5. Download all clips, write the manifest.
6. Hand off to `remotion-video` with a `video-config.yaml` if assembly is needed.

## Workflow for a lifestyle pack

1. Pick the still model (Soul V2 for editorial, GPT Image 2 for photorealism with product).
2. Train the character on reference photos.
3. Write each shot prompt with different settings, wardrobe, camera angles, but the same character_id.
4. Generate the batch. The Plus plan caps image jobs at 8 parallel.
5. Review, regenerate any shots that drift in likeness.

## Common pitfalls

- Training on photos with multiple people produces ambiguous character ID. Crop to one person before training.
- Training on heavy filter or makeup-heavy photos bakes those into the ID. Use natural photos.
- Reusing a character_id across very different stylistic models (e.g. Soul V2 then Flux 2 illustration) sometimes drifts. Stick with one stylistic family per character.
- Character IDs persist across sessions. Document them in the project manifest so the team can reuse them next quarter.

## Manifest entry for a character

```json
{
  "characters": {
    "cosmic-nexus-spokesperson": {
      "character_id": "char_abc123",
      "trained_at": "2026-05-12T10:00:00-05:00",
      "reference_images": ["ref1.jpg", "ref2.jpg", "ref3.jpg"],
      "notes": "thirty-five years old, warm features",
      "training_credits": 8
    }
  }
}
```

The skill writes this block on first training and reads it on subsequent runs in the same project.
