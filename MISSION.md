# Mission

<!--
  Owner: humans only. This file is on the protected list; the factory cannot edit it.
  When the product changes, this changes in the same commit.
-->

**Derived from:** `PRD.md`
**Last reconciled with it:** 2026-10-04

## What Workshop Gen is

Workshop Gen turns a consultant's notes on a software feature into a clear, printable
customer workshop brief. For each feature of a small manufacturer's custom software
(grouped by module such as Purchasing, Production or Warehouse) the consultant keeps
free-text notes, a preparation checklist, an ordered demonstration scenario and the
questions to ask the client, and prints one clean brief page per feature.

It is a single-user, single-deployment tool: one consultant, no accounts, one SQLite
database, server-rendered pages on the Python standard library. Those assumptions are
invariants below.

## Who it is for

- One consultant preparing client workshops, who wants to know at a glance which
  features are ready to present and to walk in with a printed brief.

Workshop Gen is not a project-management tool, a CRM, or a client portal.

## Core capabilities (in scope)

The factory may accept issues in these areas.

**Features**
- Add a feature with a name, a module and free-text notes.
- List all features grouped by module, each with its preparation progress
  ("3 of 5 ready"; a feature with no preparation items shows "0 of 0 ready").

**Brief parts**
- On a feature's page, add preparation checklist items, demonstration scenario steps
  (numbered in the order added) and discussion questions for the client.
- Tick and untick preparation items.

**The brief**
- A printable brief page per feature: title, module, notes, the checklist with its
  ticks, the numbered scenario and the questions, with no navigation.

## Out of scope -- the factory must never build this

**People and access**
- Accounts, logins, roles or per-user data. There is one consultant and no sign-in.

**Integrations**
- A connection to the customer's ERP or any other external system: import, sync or API.
- AI- or LLM-generated brief content.

**Workflow beyond the brief**
- Workshop scheduling: dates, calendars, attendees or invitations.
- Sending briefs anywhere: email, share links or a client portal.
- Templates or checklists shared or copied across features.
- File export (PDF, Word, Markdown). The browser's print of the brief page is the output.

## Hard invariants -- not tunable by any issue

1. **Standard library Python and SQLite only.** The factory's verification runs the app
   with a plain interpreter; any third-party package makes every check unrunnable.
2. **Every user value is escaped and every query is parameterized.** Notes and
   questions are free text typed by a person; they must render as text, never as markup.
3. **`/health` and `/build-id` keep working.** The factory verifies against them.
4. **The factory cannot modify governance files.** `MISSION.md`, `FACTORY_RULES.md`
   and the conventions file (`AGENTS.md`) are the constitution. A PR touching any of
   them is an automatic reject.
5. **The factory cannot modify its own judge.** `harness/`, `.factory/locks/` and
   `.factory/holdout/` define what "working" means here. Adding an assertion is
   always welcome; removing or loosening one is a human decision, always.

## Allowed evolutions

Explicitly in scope, so the factory does not reject them as architectural drift:

- New named migrations and new feature modules under `app/features/`, following `AGENTS.md`.
- Print styling for the brief page and general improvements to `app/static/style.css`.
- Refactors that move shared logic within a feature module into private helpers.

## Definition of done

**Gate 1 -- static checks and tests pass.**
`python3 -m compileall -q app tests` and `python3 -m unittest discover -s tests`.

**Gate 2 -- forms behave.** A successful POST answers a 303 redirect; invalid input
re-renders the form with a 400 and an error message; an unknown or non-numeric id is a
404. Never a 500.

**Gate 3 -- the end-to-end path passes as a real user.**

1. Start the app with `python -m app.server --port <port>` on an empty database.
2. Add a feature with a name, a module and notes.
3. On its page, add preparation items, scenario steps and questions; tick one item.
4. The brief page shows all of it, steps numbered, without navigation, and the
   feature list shows the matching "N of M ready".

This runs on every change that touches runnable code, including ones that "seem
unrelated". It is not optional.

## Open questions -- decisions nobody has made yet

These are undecided, not forbidden. **The factory may propose an answer to any of
them**, build against it, and record what it assumed. The merge is then held for a
human, so nothing ships on a guess and nothing stops for one.

- **Q1** Should features, items, steps and questions be editable or deletable? (Not in
  the MVP; the MVP only adds and ticks.)
- **Q2** In what order are modules listed on the feature list: alphabetical or by
  first use?

Once answered, an entry moves to `.factory/decisions.md` with its answer and date,
and stops being asked. **A decision is asked once.**

## What the factory does NOT own -- permanently human

- Does the brief READ well in front of a client: wording, order, tone.
- Does the printed page LOOK right: layout, page breaks, what stands out.
- Is it UNDERSTANDABLE: can the consultant use it without being told how.

The factory owns the data model, the pages and their behaviour: the layer whose
correctness can be asserted. The list above is reviewed by a human, on purpose, forever.
