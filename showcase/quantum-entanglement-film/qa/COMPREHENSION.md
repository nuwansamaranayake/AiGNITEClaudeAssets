# Beginner comprehension gate

Goal: a beginner understands entanglement from the film alone.

## Method

Three independent fresh-context agents each role-played a beginner with no physics background: Maya (13, student), Robert (67, retired, skeptical of "quantum" hype) and Aiko (30, ESL, visual-first). Each saw only the film: 52 frames sampled every 2.5 s (captions burned in) plus the timestamped narration transcript. No other files and no web were allowed. Each answered in their own words, cited the timestamps behind every answer, and listed anything that confused them.

Pass rule: every persona gets at least 6 of 7 right, and nobody leaves believing either misconception (faster-than-light messaging, or colors decided in advance).

| # | Question | A correct answer says |
|---|----------|-----------------------|
| 1 | What does "entangled" mean? | born together, linked; results always opposite, whatever the distance |
| 2 | Color before measurement? | none yet; an undecided mix of both |
| 3 | One turns blue: the partner? Distance? | gold (opposite), same instant, distance does not matter |
| 4 | One lab's results alone? | random, like coin flips |
| 5 | Why not like hidden balls in boxes? | boxes have colors set from the start; entangled particles have no hidden answer (2022 Nobel Prize) |
| 6 | Faster-than-light messages? | no: you cannot choose your result, each side sees random colors, the pattern needs notes that travel at light speed |
| 7 | Real experiment shown? | Micius satellite, 2017, entangled light to two stations 1,203 km apart |

## Result on v1

| Persona | Score | Misconceptions |
|---------|-------|----------------|
| Maya, 13 | 7 / 7 | none |
| Robert, 67 | 7 / 7 | none |
| Aiko, 30 | 7 / 7 | none |

**PASS.**

## Confusions they reported, and what v2 changed

| Confusion | Reported by | Root cause | v2 fix |
|-----------|-------------|------------|--------|
| "No color yet", but the particle looks gold (or blue) | 3 of 3 | Shader: large color patches plus a global flicker bias made one color dominate. Measured: 79% of frames were over 70% one color. | Finer color field, no global bias. Measured: 3% over 70%, 0% over 80%. Shots with undecided particles re-rendered. |
| In the slow-motion replay, A looks gold and B blue right before they turn blue and gold | 3 of 3 | Same shader cause | Same fix, plus "? Undecided" markers under both particles until the result appears |
| "Notes, at light speed" label covers Lab B's row | 2 of 3 | Label placed on the side of the path that Lab B's row occupies | Label moved to the other side of the travelling notes |
| "Ultra-secure communication" seems to contradict "no faster-than-light messages" | 2 of 3 | Term left unexplained | Sub-line: "shared secret keys that expose any eavesdropper" |
| If B changes at the same instant, something must travel faster than light | 2 of 3 | Correlation shown, carrier never ruled out on screen | "no signal passes between them" under "Same instant" |
| Closing line "Measure one. Instantly know the other." is also true of boxes | 1 of 3 | Tagline named a feature the boxes share | Tagline: "Undecided until measured. Linked across any distance." |
| "Spin" and "photons" never explained | 3 of 3 | Jargon from the narration | On-screen glosses: spin "measured as up or down"; photons "(particles of light)" |
| How experiments proved there is no hidden answer | 2 of 3 | Bell tests are out of scope for a beginner film | Kept as is. The film credits the 2022 Nobel Prize experiments (standard simplification, also upheld by the adversarial accuracy review). |

## Result on v2

Same three personas, same seven questions, fresh agents, v2 frames and transcript only.

| Persona | Score | Misconceptions |
|---------|-------|----------------|
| Maya, 13 | 7 / 7 | none |
| Robert, 67 | 7 / 7 | none |
| Aiko, 30 | 7 / 7 | none |

**PASS.** The v1 confusions about the undecided colors in the split screen, the notes label, and the closing tagline did not come back.

## Confusions on v2, and what v3 changed

| Confusion | Reported by | Root cause | v3 fix |
|-----------|-------------|------------|--------|
| In the galaxy shot the two particles already look gold and blue | 2 of 3 | That shot was not re-rendered with the v2 shader. Measured: one color covered 67 to 99% of each particle. | Re-rendered with the v2 shader. Measured: 53 to 76%. |
| The replay looks like time running backwards, and the words say "turns gold" while the particle is still mixed | 3 of 3 | The replay was marked only by a small badge | Larger badge: "Replay · same moment, slowed down" |
| "Spin" is never explained | 3 of 3 | The explanation was on screen for about 2 s and appeared after the word was spoken | Shown for about 4 s, starting before the word: "In real labs the 'color' is spin, a particle property. Measured, it is only ever up or down." |
| The glowing line looks like a wire, so how does the far one "know"? | 3 of 3 | The line was never labeled as a picture of the link | Label under the line: "The glowing line only marks the link. Nothing travels along it." The "Same instant" line now reads "no signal passes between them: the pair acts as one" |
| "Light-years" is not explained | 1 of 3 | The term was never explained | "Across the galaxy" now reads "so far that light needs 100,000 years to cross" |
| "21,000 years so far" sits on top of Lab A's row | 1 of 3 | The label sat on the side of the path where the row is | Label moved below the moving notes. It fades before it reaches Lab B's row. |
| "Ultra-secure communication" sounds like messaging, and "eavesdropper" is not a beginner word | 2 of 3 | The line did not say how the secure link works | "shared secret keys that reveal any spy listening in" plus "(the messages themselves still travel normally)" |
| How experiments proved there is no hidden answer | 1 of 3 | Bell tests are out of scope | Kept as is (same decision as v1) |

## Result on v3 (final)

Same method, fresh agents, v3 frames and transcript only.

| Persona | Score | Misconceptions |
|---------|-------|----------------|
| Maya, 13 | 7 / 7 | none |
| Robert, 67 | 7 / 7 | none |
| Aiko, 30 | 7 / 7 | none |

**PASS.** Nobody reported the galaxy colors, the notes label, the light-year distance or the secure-communication line again. All three now name the replay themselves and say it took them a moment.

What still puzzles them, and why the film leaves it:

| Question | Reported by | Decision |
|----------|-------------|----------|
| If nothing travels between them, how does the partner "know"? | 3 of 3 | Kept. This is the real open question of entanglement. Standard physics gives no mechanism beyond the correlation. The film states what is known ("no signal passes between them: the pair acts as one") and does not invent a mechanism. |
| How did experiments prove there is no hidden answer? | 3 of 3 | Kept. Bell tests need statistics across different measurement settings, which is beyond a 130-second beginner film. |
| What is spin, and is blue up or down? | 3 of 3 | Kept. The on-screen line explains what matters here: spin is a particle property, and a measurement gives only one of two results. Mapping colors to up or down adds a detail the film does not use. |
