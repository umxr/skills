---
tags: [skill-creator]
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, Agent]
---

/inspect-codebase reconciliation logic

next sprint I have to change how ledgerline matches bank lines to invoices. before I touch anything I want a proper look at the whole service and especially the reconciliation path - what calls it, what could break, what's tested.

Input files: the ledgerline Python service (pyproject.toml, requirements.txt, src/, tests/, alembic/, Dockerfile, Makefile)
