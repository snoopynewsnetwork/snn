# 2026 Senate state research dispatch

Requested **2026-10-17**: reproduce the Michigan research for every state in
the [35-race Senate index](senate/2026/README.md), with direct commits and pushes
to main. Michigan is complete; **34 other state stacks are queued**. This is a
dispatch record, not a claim that the new research is complete.

The [common brief](senate/2026/RESEARCH_BRIEF.md) specifies the original four
questions, geographic win targets, local news and NYT backstops, live polling
strategy, actual map assets, provenance and validation. The durable work list
is [research-queue.json](senate/2026/research-queue.json).

Paseo has no configured profiles. Provider discovery confirmed
`codex/gpt-6.1-sol`, `full-access`, and `xhigh` reasoning, matching the initiating
agent. A batch coordinator dispatches four state-specific question agents per
queued state, with at most two workers active concurrently. The coordinator
reviews and publishes each completed state. This keeps at most four active
agents including the initiating conversation. Workers never change Git.

State order prioritizes competitive races, then covers the remaining states.
State-specific reporting geography, election rules and independent challengers
must be handled explicitly. Current rules require official verification.

## Coordinator

Launch pending. The initiating agent will record the actual Paseo ID here and
in the queue. The coordinator will record each state's actual worker IDs in
its `research-dispatch.md` and in the queue, and published commit IDs as state
packages finish.

## Progress

Michigan complete at dispatch. All other states queued. Consult the queue for
current state status. Completed packages will be linked from their state README
files and pushed incrementally to main.
