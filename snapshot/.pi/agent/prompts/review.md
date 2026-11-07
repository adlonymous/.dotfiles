---
description: Review current changes for bugs and quality issues
argument-hint: "[focus]"
---
Review the current repository changes. Use `git status` and relevant diffs.

Focus on: ${ARGUMENTS:-bugs, correctness, security, error handling, maintainability, and test coverage}.

Return:
- Critical issues
- Non-blocking suggestions
- Tests/checks to run
- A short verdict
