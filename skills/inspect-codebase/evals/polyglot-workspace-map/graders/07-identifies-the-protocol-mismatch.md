---
type: llm
focus: trace
weight: 1
---

The report identifies the protocol mismatch: the gateway writes raw bytes without the u32 length prefix that relay-core's framing expects
