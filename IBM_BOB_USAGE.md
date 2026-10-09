# IBM Bob configuration

This project uses six custom modes from [`.bob/custom_modes.yaml`](.bob/custom_modes.yaml).
The Markdown role files in [`agent-config/agents/`](agent-config/agents/) explain
the configuration; they do not replace it.

## Modes and file permissions

| Mode | Output |
|---|---|
| Research | `design_brief.md` |
| Coding | Application files under `app/` |
| Review | `review_report.md` |
| Testing | `app/test_*.py` and `test_report.md` |
| Debug | `debug_report.md` |
| Pitch/Docs | `app/README.md` and `docs/demo-script.md` |

Each mode defines `slug`, `name`, `roleDefinition`, `whenToUse`,
`customInstructions` and capability `groups`. The edit group's `fileRegex`
restricts edit-tool paths. Read/execute permissions are separate capabilities;
an edit-path rule alone is not a sandbox for arbitrary execution.

For example, the Testing mode's edit regex includes both test files and the
root report. Omitting the report path initially prevented the mode from writing
one of its required outputs; see [lessons learned](docs/lessons-learned.md).

## Operating the workflow

1. A team member selects Research and reviews its updated brief.
2. Coding implements the brief; Review records approval or requested changes.
3. Testing writes/runs checks independently of the Coding role.
4. Failures go to Debug, then Coding and a new review/test pass.
5. A passing run can proceed to documentation.

The [controller](workflow/handoff_controller.py) checks the prior stage's files,
allows a defined transition, requires an approver name and appends a JSONL record.
The team member then selects the displayed Bob mode. It does not automate the
Bob UI or invoke an unsupported orchestrator.

```sh
python workflow/handoff_controller.py status
python workflow/handoff_controller.py handoff review testing --approved-by "Team member"
```

The second command writes an approval record; use a real approver only when that
transition has been reviewed. A name in a local log is not authenticated identity
or an immutable enterprise audit system.

## Evidence and CI

Root reports are the current agent-produced inputs. The hand-off log preserves
recorded transitions. CI runs pytest against source; it does not run the local
Bob modes. Concrete recorded findings live in the review/debug reports, while
the [lessons document](docs/lessons-learned.md) retains the project history.

Current results must be associated with the revision tested. The static dashboard
only replays a recorded demonstration. It is not live verification of new commits.
