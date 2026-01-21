# Session Management Protocol

## Session Initialization (The "Discovery" Phase)

Before performing any development tasks, the agent must establish the current state of the project by performing the following steps:

1.  **Branch Audit**: Run `git branch -a` and `git log --branches --not --remotes` to identify all local and remote branches.

2.  **Identify the "Lead" Branch**:
    *   Locate the branch with the most recent commit timestamp.
    *   If a branch follows a numbering convention (e.g., `phase-1`, `task-2.1`), prioritize the highest version number unless a more recent commit exists on a different feature branch.

3.  **Synchronization**:
    *   Create a new session branch for the current 3-hour window (e.g., `jules-session-[timestamp]`).
    *   Pull/Merge all commits from the identified "Lead" branch into the current session branch to ensure no work is lost.

4.  **Context Acquisition**:
    *   **The Master Plan**: Read all files in `docs/plan/`.
        *   If the plan is phased (1, 2, 3...), identify the current phase by comparing the plan against the existing codebase.
        *   If the plan is architectural, ensure all code changes align with the defined architecture/patterns.
    *   **The Handoff File**: Read `HANDOFF.md` in the root directory. This is the primary source of truth for what the previous session achieved.
    *   **Prove Continuity**: Before writing a single line of code, you must prove you have found the latest work from the previous agent by summarizing the last `HANDOFF.md` in your logs.

## Execution Guidelines

1.  **Strict Adherence**: Follow the `docs/plan/` instructions meticulously. Do not deviate from the architectural or phased requirements unless a blocker is identified.
2.  **Atomic Commits**: Commit work in logical increments with descriptive messages, including the timestamp of the commit.

## Session Conclusion (The Handoff)

At the end of the session, or when the 3-hour limit approaches, the agent must update or create a `HANDOFF.md` file. This file acts as the bridge for the next agent session.

The `HANDOFF.md` structure must include:

*   **Current Branch**: The name of the branch where the latest work resides.
*   **Latest Commit**: The SHA and timestamp of the final commit of this session.
*   **Achievement Summary**: A bulleted list of specific tasks from `docs/plan/` that were completed.
*   **State of Play**: Where exactly the next agent should start (e.g., "Starting Phase 2, Step 4: Database Migration").
*   **Blockers/Notes**: Any issues encountered that prevented completion of the planned tasks.
