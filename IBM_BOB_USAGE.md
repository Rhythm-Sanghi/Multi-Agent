# How We Used IBM Bob

This document is a full account of how IBM Bob was actually used to build this project, including the parts of the platform we relied on, the workflows we developed, and a few things we got wrong along the way and had to correct. It's written to be read on its own, without needing the rest of the repo open at the same time, though the actual files it references (`.bob/custom_modes.yaml`, `design_brief.md`, `review_report.md`, `test_report.md`, `debug_report.md`) are all sitting right next to it if you want to see the real output.

## The core idea

The assignment was to build multiple IBM Bob agents that collaborate — a research agent, a coding agent, and a testing agent, working together the way a small software team would. We took that as a genuine design constraint rather than something to satisfy minimally. Instead of one general-purpose AI writing code end to end, we wanted six agents, each doing one job, each unable to do any other agent's job, handing off to each other through plain files that any of us could open and read at any point.

Bob turned out to be a good fit for this specifically because of how its custom mode system works, which we'll walk through in detail below.

## Bob's built-in modes, and where they weren't enough

Bob ships with three built-in modes: **Agent** mode for writing and modifying code, **Plan** mode for architecture and design work before code gets touched, and **Ask** mode for read-only explanations without making any changes. We used Ask mode constantly in the early stages, mostly to interrogate Bob about its own platform (more on that below), and Plan mode briefly when we were first sketching out the API's design.

But none of the three built-in modes give you a *persona* — a role, a fixed set of behavioral rules, and a locked-down set of permissions that persist across a conversation. Agent mode can do anything you ask it to, which is exactly the opposite of what we needed for something like a Testing Agent that should never, under any circumstance, be able to edit application source code.

## Custom modes: the actual mechanism

The real feature that made this project possible is Bob's custom modes system, configured through a file called `custom_modes.yaml` inside a hidden `.bob` folder at the project root. We didn't know this file existed at first — we initially wrote our agent specifications as plain markdown files in `agent-config/agents/`, assuming Bob would somehow pick them up automatically. It doesn't. Those markdown files are useful as human-readable documentation, but Bob itself only reads `.bob/custom_modes.yaml`.

Each entry in that file defines one custom mode, and each custom mode is effectively one agent. A mode definition has five parts:

- **slug** — an internal identifier (letters, numbers, hyphens only), like `research-agent` or `debug-agent`
- **name** — a display name shown in Bob's mode selector
- **roleDefinition** — the core identity of the agent. This is the closest thing to a system prompt. It describes who the agent is, what its one job is, and explicitly what it must not do.
- **whenToUse** — a short description of when this mode is the right one to use. This matters more than it sounds like it should, because it's what Bob's routing logic (and, in our case, our own manual reasoning about which mode to switch to) uses to decide which agent belongs at which point in a workflow.
- **customInstructions** — the specific, mechanical rules the agent should follow: what file to write, what format that file should be in, what it should never touch.
- **groups** — the actual tool-permission configuration. This is a list of capability groups (`read`, `edit`, `execute`, `mcp`, `skill`, `todo`, `subtask`) that the mode is allowed to use. The `edit` group can additionally be scoped to a specific file pattern using a regular expression.

That last part, the `fileRegex` scoping inside the `edit` group, is the single most important technical detail in this whole project, so it's worth showing exactly what it looks like. Here's the real configuration for our Coding Agent:

```yaml
groups:
  - read
  - - edit
    - fileRegex: "^app/.*"
      description: app/ directory only
  - execute
  - skill
  - todo
  - subtask
```

That `fileRegex: "^app/.*"` line means Bob will refuse to let this mode write to any file outside the `app/` directory, at the tool level, before the agent's own judgment ever comes into play. We didn't have to trust that Coding Agent would *choose* to respect the boundary between application code and test files or documentation. Bob enforces it structurally. Similarly, our Testing Agent's `edit` permission is scoped to `^app/test_.*\.py$` — it can write test files, and nothing else, not even by accident.

We found out how strict this enforcement actually is the hard way. Early on, our Testing Agent tried to write `test_report.md` at the project root as part of its job, and Bob blocked it, because that path didn't match the `fileRegex` we'd configured. The agent itself told us plainly that it couldn't write the file and explained exactly why. We had to go back and widen the pattern to `^(app/test_.*\.py|test_report\.md)$` before it could do the full job we'd actually asked of it. That's a small example, but it's a real one, and it taught us something worth stating directly: when you scope an agent's permissions, you have to think through every artifact it needs to produce, not just the source code you want to keep it away from.

## Our actual six agents

We ended up with six custom modes, added incrementally rather than all at once, each one only added once the previous stage of the pipeline had proven itself.

**Research Agent** reads a feature request or our locked scope document (`docs/scope.md`) and writes `design_brief.md` — a structured breakdown of data model, endpoints, libraries, and edge cases. Its permissions only allow it to edit that one file. Across three separate feature requests, it correctly carried forward every constraint from earlier runs (no ORM, `sqlite3` only, the SQLite `INTEGER`-to-Python-`bool` conversion detail) without us having to repeat ourselves, which told us the "living design brief" pattern actually holds up across multiple sessions and isn't just a first-run coincidence.

**Coding Agent** reads `design_brief.md` and implements exactly what it specifies inside `app/`. When we later introduced a Review Agent and a Debug Agent whose job was to send it feedback, Coding Agent consistently applied only the specific fix requested rather than refactoring unrelated code, which mattered a lot once multiple agents were feeding it corrections in sequence.

**Review Agent** reads Coding Agent's output and writes `review_report.md`, checking for security issues, scope violations, and code quality problems before Testing Agent even runs. This is the agent that produced our most concrete finding: on its very first real pass against code we'd already shipped and marked as tested, it found that a `PUT` handler was building part of its SQL query using an f-string with column names inserted directly into the string, rather than using safe parameterization. The actual values passed by users were parameterized correctly, but the column names weren't, and since those column names happened to be hardcoded today, there was no live exploit — but the pattern itself was flagged as a real risk, because one future change to that code could have turned it into a genuine SQL injection vulnerability. We had Coding Agent rewrite that handler to use fixed, static SQL statements instead of one dynamically built string, and Review Agent verified the fix on a second pass before issuing an APPROVED verdict. Review Agent also separately caught that our own locked `docs/scope.md` had drifted out of sync with what we'd actually built and approved, which led us to formally version it as scope v2 rather than leave a "locked" document that quietly wasn't accurate anymore.

**Testing Agent** writes and runs its own test suite independent of anything Coding Agent may have written for itself, specifically so the same agent isn't grading its own work. It produced 13 tests covering every endpoint's happy path, every 404 case, and boundary conditions on input validation, and its permission scope means it can write test files and its own report but cannot touch application source at all.

**Debug Agent** was added once we realized every one of our first several pipeline runs had passed cleanly, which meant we'd never actually exercised the failure-and-recovery path. We deliberately introduced a real bug — changed the `DELETE` endpoint to return the wrong HTTP status code — and had Debug Agent diagnose the resulting test failure before handing it to Coding Agent. It correctly classified the issue as a genuine application bug rather than a bad test, traced the problem to two separate hardcoded references to the wrong status code (not just the more obvious one), and gave Coding Agent a precise two-line fix instruction instead of forwarding the raw pytest error and hoping for the best. This is genuinely the clearest evidence in the whole project that a dedicated diagnosis step adds value beyond what a raw error message alone provides.

**Pitch/Docs Agent** runs only after Testing Agent reports a passing suite, and turns the accumulated `design_brief.md`, `review_report.md`, and `test_report.md` into a finished `app/README.md` and `docs/demo-script.md`, written for someone outside the project entirely. Its first draft of the README's "how to run this" instructions genuinely failed the first time we tested it, though it later turned out the instructions were correct and we had simply run the command from the wrong working directory. We only caught that distinction because we tested the instructions ourselves rather than trusting them on sight, which became one of our clearer lessons about verifying agent output instead of just reviewing it visually.

## Our actual workflow, mode by mode

For every feature request, our process was:

1. Switch to **Research Agent** mode, describe the feature, let it read the current scope and write or update `design_brief.md`
2. Read `design_brief.md` ourselves before proceeding, checking it against prior decisions we'd already locked in
3. Switch to **Coding Agent** mode, point it at `design_brief.md`, and restate any implementation-level constraints that weren't the Research Agent's job to specify (for example, "use pytest's `tmp_path` fixture for test database isolation" is a testing concern we told Coding Agent directly, since it wasn't something that belonged in the design brief itself)
4. Switch to **Review Agent** mode, let it read the diff and produce `review_report.md`
5. If Review Agent's verdict was CHANGES REQUESTED, switch back to Coding Agent with the specific findings, then back to Review Agent for a second pass
6. Once APPROVED, switch to **Testing Agent** mode to write and run an independent test suite
7. If tests failed, switch to **Debug Agent** mode for a root-cause diagnosis before handing the failure back to Coding Agent
8. Once tests passed, switch to **Pitch/Docs Agent** mode only at the very end, to produce final documentation

Every one of those mode switches was done manually, by us, clicking the mode selector or using Bob's slash-command shortcut for switching. We want to be direct about that because we initially assumed there was a more automated way to do it, and it's worth explaining exactly what happened there.

## The Orchestrator mode correction

Partway through the project, we asked Bob's own chat directly whether there was a way to automatically chain our custom modes together instead of switching between them by hand. Bob answered in detail, describing a built-in "Orchestrator mode" that reads the `whenToUse` field on custom modes to decide how to delegate work automatically, and gave us a full comparison table contrasting it with a `switch_mode` tool it said could also handle mid-task mode transitions.

We built part of our plan around this before verifying it. When we actually went looking for Orchestrator mode in the mode selector, it wasn't there. We asked Bob to double-check itself, and it directly reversed its earlier answer, confirming that only three built-in modes exist — Agent, Plan, and Ask — and that Orchestrator mode was never a real, shipping feature. We're including this in as much detail as the rest of this document because it's a genuinely important finding in its own right: an AI tool's own chat interface can describe its own product incorrectly, with full confidence and convincing supporting detail, and the only way we caught it was by checking the actual product rather than taking the answer at face value. We went back to manual mode switching after that, and it worked reliably across every subsequent run — enough that we stopped thinking of it as a fallback and started treating it as simply the correct way to use the tool for this kind of workflow.

## What Bob was, and wasn't, doing under the hood

To be precise about where the actual intelligence in this project came from: Bob's underlying model routing, tool-calling, and file-access execution is what carried out every instruction we gave each custom mode. The custom mode configuration is what gave each of those six agents a distinct identity, a fixed job, and an enforced permission boundary — without that layer, we would have had one general-purpose assistant doing everything, which is precisely the pattern this whole project was designed to move past.

We did not use Bob's CLI (BobShell) for any of this, despite an earlier point in the project where we assumed we would. We discovered that BobShell either wasn't installed or wasn't on our system PATH, and once we confirmed we were working entirely through the Bob IDE's chat panel rather than a terminal, we abandoned the CLI-based approach entirely rather than force it. A PowerShell controller script we wrote early on for that abandoned approach was removed from the final repository, since keeping it in would have implied automation that never actually ran.

## Where CI fits in, and where it doesn't overstate what Bob does

We wired up GitHub Actions to run our actual pytest suite automatically on every push. It's worth being precise that this is not Bob's agents running in the cloud — GitHub Actions runs on GitHub's own servers and has no access to our local Bob IDE session or its custom modes. What CI actually does is run the real test file that our Testing Agent wrote, the same way anyone's local machine would. We verified this genuinely works, not just in theory, by deliberately pushing two separate broken versions of the code at different points in the project and watching the Actions tab go red both times, then confirming it went green again after reverting. We think this distinction matters enough to state clearly here rather than let it blur into an overstated claim about Bob-in-the-cloud.

## Summary

In total, Bob's custom mode system is what let us build six agents with genuinely separate identities and genuinely enforced permission boundaries, coordinate them through a real multi-stage software development workflow, and produce evidence — a caught security issue, a caught scope drift, a caught and precisely diagnosed bug — that the approach adds real value over a single generalist pass. Every hand-off between our agents exists as a plain markdown file in this repository. Nothing described in this document happened invisibly; it's all sitting in the commit history and the files next to this one.