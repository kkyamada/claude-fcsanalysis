---
description: Compact conversation and save to logs/ directory with timestamp
argument-hint: [focus-instructions]
---

Use the `/compact` command to compress the current conversation and save it to the logs/ directory.

Generate a filename using this pattern:
- Base filename: `logs/compact-{YYYYMMDD-HHMMSS}.md`

If focus instructions are provided in "$ARGUMENTS", use them to guide what should be preserved during compaction.

Execute: `/compact $ARGUMENTS` (if arguments provided) or `/compact` (if no arguments)

After compaction completes, the conversation history will be compressed while preserving important context.

Where {YYYYMMDD-HHMMSS} is the current timestamp in format: year-month-day-hour-minute-second
