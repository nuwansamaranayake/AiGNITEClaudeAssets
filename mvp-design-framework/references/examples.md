# Worked Examples

One-line summary: Three MVPs run through the five questions, showing acceptable answers and the rejections each one survived.

## Example 1: Habit Tracker

### Question 1: Core function

Acceptable answer: "marks a daily habit as done"

Rejected first answer: "tracks habits with reminders, streaks, social sharing, and AI insights" - too many functions, reject and ask for the single load-bearing outcome.

### Question 2: Core loop

Acceptable answer: "user taps the habit row, the row fills with green, the streak counter increments with a haptic pulse, all inside three seconds of cold start"

Rejected first answer: "user opens the app and sees their habits" - no action, no sensory feedback.

### Question 3: Accessory features

Acceptable answer:
1. Streak history graph (amplifies the streak motivation)
2. Habit reminder at a chosen time (re-entry to the loop)
3. Streak freeze tokens earned weekly (forgiveness mechanic that protects the streak)

Rejected first answer: 1) graph, 2) reminders, 3) social sharing, 4) Apple Health sync, 5) export to CSV - too many. Asked the user to cut to three.

### Question 4: Surface area

Acceptable count: six screens.
1. Today (core loop)
2. Habit detail
3. Stats
4. Add habit
5. Settings
6. Sign in

### Question 5: Retention hook

Acceptable answer: "a streak that resets to zero if the user misses a day"

Rejected first answer: "push notifications at 9am" - channel without state. The follow-up surfaced the streak-reset state.

## Example 2: Calorie Tracker

### Question 1: Core function

Acceptable answer: "logs a meal"

### Question 2: Core loop

Acceptable answer: "user taps the plus button, types or photographs the meal, sees the calorie total update with a smooth animation and the daily ring fill more, inside fifteen seconds"

### Question 3: Accessory features

Acceptable answer:
1. Daily calorie goal ring (gives the log a target)
2. Photo-to-calories AI estimate (cuts log friction)
3. Yesterday comparison (frames today against yesterday)

### Question 4: Surface area

Acceptable count: five screens.
1. Today's log
2. Add meal
3. Photo capture
4. Goal settings
5. Sign in

### Question 5: Retention hook

Acceptable answer: "an incomplete daily ring at 8pm"

Rejected first answer: "weekly email summary" - wrong channel, wrong cadence. The follow-up surfaced the incomplete-ring state.

## Example 3: Pomodoro

### Question 1: Core function

Acceptable answer: "runs a 25-minute focus timer"

### Question 2: Core loop

Acceptable answer: "user taps the big circle, it fills clockwise as the timer counts down, when the timer ends the phone vibrates twice and a chime plays, all within two seconds of opening the app"

### Question 3: Accessory features

Acceptable answer:
1. Session log (visible record of completed pomodoros today)
2. Five-minute break timer (the other half of the pomodoro pattern)
3. Daily target count (frames the day as a goal)

### Question 4: Surface area

Acceptable count: four screens.
1. Timer
2. Session log
3. Settings
4. Sign in

### Question 5: Retention hook

Acceptable answer: "an unmet daily pomodoro target visible on the lock-screen widget"

Rejected first answer: "reminder notifications" - too vague. The follow-up named the target-shortfall state.

## What every example shares

- One verb-plus-object core function
- A sub-thirty-second loop with both action and feedback named
- Exactly three accessories, each tied to the core loop
- Seven or fewer screens
- A retention hook stated as a state, not a channel
