# Codex Context And Storage Workflow

## Purpose

Keep project continuity in small repository documents instead of relying on one long Codex conversation or
reloading archived session JSONL files.

## Session Start

1. Read `CURRENT_SESSION_CONTEXT.md`.
2. Read `../progress/README.md` and the latest progress file.
3. Read only the plan/report/source file needed for the current gate.
4. Run `git status --short -- Projects/Tracked_Mobile_Robot` and inspect the latest project commit.

Use `PROJECT_MEMORY.md`, older handoffs, and archived conversations only to resolve a missing fact or conflict.

## During Work

- Keep one gate or tightly connected milestone in one conversation.
- Store logs, captures, PDFs, and diagrams as files, then discuss their paths and relevant excerpts.
- Do not attach the same image repeatedly. Do not paste complete build logs when the failing or measured section
  is enough.
- For bench work, state the goal once, give one action, wait for the result, and advance after `통과 다음`.
- Accumulate factual results and write progress/evidence once at the end of the work block.

## Session Closeout

Before moving to a new conversation:

1. Update the dated progress/evidence documents once.
2. Replace the status and next action in `CURRENT_SESSION_CONTEXT.md`.
3. Update `docs/progress/README.md` or `docs/handoff/README.md` only when their current pointer changed.
4. Commit/push only when requested for that work block.
5. Start the next conversation with `NEXT_SESSION_START_PROMPT.md`.

## Conversation Archive

The raw archive is external to the repository:

- Archived JSONL: `D:\CodexSessionArchive\sessions`
- Text index: `D:\CodexSessionArchive\indexes\codex_text_index.sqlite`
- Index builder: `D:\CodexSessionArchive\index_codex_sessions.py`

The 2026-09-08 index covered 185 unique archived/local sessions and 51,249 JSONL messages plus 2,462
high-quality projected messages from the local thread database. It excluded 36 duplicate session copies and
large image/state lines. Some older archived Korean text already contains replacement characters; use the
dated repository documents created from those sessions as the authoritative record.

The project must remain usable when D: is disconnected. Do not make build, test, or documentation links depend
on the external index.

## Storage Snapshot And Policy

On 2026-09-08 Windows saw only the internal 256 GB NVMe and a 233 GB SanDisk USB drive mounted as D:.
The separate Ubuntu 500 GB SSD was not visible to Windows. C: had about 70.1 GB free; local Codex JSONL files
used about 2.68 GB. D: had about 49.8 GB free; the raw Codex archive used about 53.29 GB and the text index
about 95 MB.

Do not move or delete an active session while Codex is open. Future cleanup should close Codex, identify the
active rollout, hash-verify the archive copy, then remove only verified old local copies. Raw archive deletion
or deduplication is a separate storage-maintenance task.
