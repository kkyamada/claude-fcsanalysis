---
description: Export conversation to logs/ directory with timestamp
argument-hint: [filename-prefix]
---

Use the `/export` command to save the current conversation to the logs/ directory.

Generate a filename using this pattern:
- If no argument provided: `logs/export-{YYYYMMDD-HHMMSS}.md`
- If argument "$1" provided: `logs/$1-{YYYYMMDD-HHMMSS}.md`

Execute: `/export logs/{filename}`

Where {YYYYMMDD-HHMMSS} is the current timestamp in format: year-month-day-hour-minute-second
