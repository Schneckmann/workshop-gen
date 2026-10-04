# PRD: Workshop Brief Builder

## Problem
A consultant building custom software for a small manufacturer has detailed notes on every
feature, but turning them into a clear customer workshop takes hours each time: what to
prepare, how to demonstrate it, and what to ask the client.

## Who it is for
One consultant preparing client workshops. No accounts.

## What it does (MVP)
1. **Features.** Add a feature with a name, the module it belongs to (for example
   Purchasing, Production, Warehouse) and free-text notes. A list shows all features by
   module.
2. **Brief parts.** On a feature page, add items to three lists: preparation checklist
   items, demonstration scenario steps (in order, numbered), and discussion questions for
   the client. Each preparation item can be ticked off and unticked.
3. **The brief.** A printable brief page for one feature: title, module, notes, the
   checklist with ticks, the numbered scenario and the questions, without navigation. The
   feature list shows each feature's preparation progress as "3 of 5 ready".

## Out of scope for the MVP
Accounts or logins, connecting to the customer's ERP, AI-generated briefs (a later lap),
scheduling workshops, emailing briefs, templates shared across features.

## Constraints
Standard library Python + SQLite only (see AGENTS.md). Server-rendered pages.
