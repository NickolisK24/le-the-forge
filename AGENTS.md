\# le-the-forge Codex Instructions



This project prioritizes correctness, deterministic behavior, testability, and debuggability over visual polish.



\## Git and GitHub Rules



All Git/GitHub-visible work should appear authored and maintained by Nikko.



Do not mention Codex, ChatGPT, OpenAI, AI, agents, bots, generated-by tooling, or co-authored-by AI metadata anywhere in GitHub-visible output.



Do not create branches using:

\- codex/\*

\- ai/\*

\- agent/\*

\- bot/\*

\- generated/\*



Use project-focused branch names:

\- feat/affix-source-diagnostics

\- fix/bundle-loader-guards

\- docs/forge-migration-tracker

\- test/production-non-consumption



Commit messages must be concise, human, and project-focused.



\## Project Priorities



Prioritize extraction pipeline correctness first.



Do not over-polish UI or formatting unless it supports validation, debugging, or user-facing clarity.



When changing extraction, migration, planner, simulator, or stat logic:

\- preserve backward compatibility where possible

\- add or update tests

\- add debug output when it helps validate correctness

\- avoid inferred game mechanics unless explicitly marked experimental

\- keep stable verified logic separate from experimental logic

