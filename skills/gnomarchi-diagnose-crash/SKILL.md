---
name: gnomarchi-diagnose-crash
description: Diagnose a crash from coredumpctl; decide upstream report; offer mute.
---

# gnomarchi-diagnose-crash

Use `coredumpctl info <pid>`, symbolize if possible, summarize root cause, and offer `gnomarchi agent crash mute <binary>`. Do not delete cores unless asked.
