# Why This Framework

One-line summary: The reasoning behind the five MVP questions and why each one stops a common failure mode.

## The problem this solves

Solo founders building mobile apps fail at three points:

1. They ship a feature set instead of a function. The app does many things, none well.
2. They optimize the wrong loop. The first thirty seconds are slow and unrewarding, so retention dies.
3. They keep adding screens. By week six the app has twenty-three screens and the team is paralyzed.

The five questions cut these failures off at the design step, before code exists.

## Question by question

### Why "the one thing this app does"

If you remove the one thing and the app still works, then the one thing is not load-bearing. Either it should be the load-bearing function, or the app has no clear identity.

This question forces the founder to pick one outcome and defend it. Every other feature lives or dies based on whether it amplifies this one outcome.

The failure mode: a founder writes "tracks hydration, reminds users, gamifies progress, syncs with Apple Health". Four functions, no center. The app becomes a settings page with a logo.

### Why "thirty seconds, action plus reward"

Retention is decided in the first session. Within thirty seconds of opening a new app, the user has formed an opinion. If they did something and got a satisfying response, they come back. If they tapped around looking for the action, they uninstall.

The question forces the founder to name both halves: the action the user takes and the sensory feedback they receive. Tap a button is not enough. Tap a button and see the daily streak count up by one with a haptic pulse and a green flash is enough.

### Why "exactly three accessory features"

Three is small enough to ship. Three is large enough to make the core loop sticky. Three accessory features supporting one core function gives the team four things to perfect over four weeks.

More than three accessories means the founder has not chosen. They want the safety of optionality. The cost of that safety is shipping nothing well.

### Why "seven screens or fewer"

Seven screens covers a tab bar with five tabs, one detail screen, and one settings screen. Or three tabs plus four detail or modal flows. Either way it fits in a single mental map.

Past seven screens the team loses the ability to test every path manually. Bugs hide. Onboarding gets long. The app stops feeling like one app and starts feeling like a portal.

### Why the retention hook is a state, not a channel

Push notifications open the app. The state pulls the user back. A push notification with no underlying unfinished state produces a one-time tap and an immediate uninstall. The same push notification pointing to a streak the user wants to defend produces a daily session for a year.

Founders default to "we will send push notifications" because the channel is concrete and the state is hard. The skill rejects the answer to force the harder thinking.

## The cost of skipping this step

Two failures from real AiGNITE projects:

- A water intake app shipped with fourteen screens, three competing core functions, and "push notifications" as the retention plan. Retention at day seven: four percent.

- A compliance tracking app shipped with one core function and a working core loop, but no accessory features. Users completed the core action twice and uninstalled. The function worked. The hook did not exist.

Both failures map directly to a skipped question in this framework.

## When to break the rules

This is a framework, not a law. Break a rule when:

- The domain demands it. A medical compliance tool with regulatory disclosure screens may exceed seven screens. Document the deviation in the MVP_SPEC.md.
- The team has shipped three apps using the framework and has learned where it fails for their specific market.

Never break a rule on the first app. Run the framework strictly. Earn the right to deviate.
