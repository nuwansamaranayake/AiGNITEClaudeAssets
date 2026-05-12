---
name: mvp-design-framework
description: Forces five-step MVP discipline before any mobile app code gets written. Asks five sequential questions covering core function, core loop, accessory features, surface area, and retention hook, then outputs a one-page MVP spec. Use this skill whenever the user mentions designing a new app, scoping an MVP, planning a mobile project, asking what an app should do, feature planning, or asking for help with an app idea, even if they do not name the skill by name.
---

# mvp-design-framework

## Purpose

Stop premature coding. Force five framing questions before any scaffold runs. Output a one-page MVP_SPEC.md the rest of the suite consumes.

## When to trigger

Trigger on these user phrases. Match loosely.

- "design a new app"
- "MVP"
- "app idea"
- "scope a mobile app"
- "feature plan"
- "what should this app do"
- "help me design"
- "design framework"
- "I want to build an app"

## Behavior

Run the five questions in order. Refuse to proceed to question N+1 until question N has a concrete answer. Generic answers are rejected with a follow-up. After all five answers, write MVP_SPEC.md to the project root and print a summary.

## The five questions, asked verbatim

### Question 1: Core function

"What is the one thing this app does that, if removed, would mean the app is no longer the app?"

Reject if the answer:

- Names more than one capability
- Names a technology rather than a user outcome ("uses AI", "has Stripe billing")
- Names a feature rather than a function ("dark mode", "social login")

The answer is a single user outcome stated as a verb plus object. Example: "logs water intake". Not "tracks hydration with reminders and graphs".

### Question 2: Core loop

"What is the action the user takes, and the visual or haptic reward they get, inside thirty seconds of opening the app?"

The answer names an input action and a sensory feedback within thirty seconds of cold start. If the feedback is "they see their data", reject and ask what the data looks like and what makes it satisfying to see.

### Question 3: Accessory features

"What three accessory features support that core loop without bloating it?"

Exactly three. No more, no less. Each accessory feature must directly amplify the core loop, not introduce a parallel loop. Reject lists longer than three by asking the user to cut.

### Question 4: Surface area

"Count the screens. If the answer is more than seven, what cuts?"

Hard cap: seven screens including onboarding and settings. Refuse to proceed past this question with an eight-screen plan. Ask the user to merge or remove screens until the count is seven or fewer.

### Question 5: Retention hook

"What unfinished state pulls the user back tomorrow?"

Reject "push notifications" as the answer. Push notifications are a channel, not a hook. The hook is the unfinished state the notification refers to. Example: a streak that resets if the user skips a day. Example: a reading the user has not opened yet. Example: a question the user has not answered.

## Output

After all five answers pass validation, write `MVP_SPEC.md` at the current working directory. Use the template at `assets/templates/MVP_SPEC.md.template`. Substitute the five answers into the file.

Print a short summary:

```
MVP_SPEC.md written.
Core function:    <answer 1>
Core loop:        <answer 2>
Accessories:      <3 items>
Screens:          <count>
Retention hook:   <answer 5>

Next: run mobile-app-scaffold to start the project.
```

## Hard constraints

- Seven-screen ceiling. No exceptions.
- Retention hook is a state, not a channel.
- Accessory features count is exactly three.
- The core function is one user outcome, not many.

## Composes with

- Runs before `mobile-app-scaffold`.
- Runs before `mcp-to-mobile` when the MCP-driven app needs scope discipline.

## References

- [references/why-this-framework.md](references/why-this-framework.md) explains the reasoning.
- [references/examples.md](references/examples.md) shows three worked examples.
