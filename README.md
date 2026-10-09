# Multi-Agent software workflow

An IBM Bob custom-mode demonstration: six roles research, implement, review,
test, debug and document a small FastAPI to-do API. Team members select the Bob
mode and approve hand-offs; the Python controller checks evidence and records
those transitions. It does not launch or switch the Bob modes itself.

## Run the API

```sh
python -m venv .venv
```

Activate the environment, then run from the repository root:

```sh
python -m pip install -r app/requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. See [the API guide](app/README.md) for endpoints.

```sh
python -m pytest app/test_main.py workflow/test_handoff_controller.py -v
python workflow/handoff_controller.py status
```

## Workflow

Research → Coding → Review → Testing → Docs. On a failed test pass, Debug
records a diagnosis before the work returns to Coding.

- [`.bob/custom_modes.yaml`](.bob/custom_modes.yaml): executable custom-mode configuration.
- [`agent-config/agents/`](agent-config/agents/): human-readable role prompts.
- [`IBM_BOB_USAGE.md`](IBM_BOB_USAGE.md): configuration and file permissions.
- [`docs/workflow/README.md`](docs/workflow/README.md): controller gates and audit trail.

The root design brief, review, test and debug reports are agent-produced workflow
inputs. They remain at the paths required by the controller and mode definitions.
They are recorded evidence, not a live execution status or independent audit.

## Recorded findings

- [Review report](review_report.md): fixed SQL statements replaced a risky dynamic
  update pattern; the recorded finding does not establish an exploitable shipped injection.
- [Debug report](debug_report.md): diagnosis of a deliberately introduced DELETE
  response-code mismatch.
- [Lessons learned](docs/lessons-learned.md): permission-scope and documentation
  mistakes encountered during the project.

Use current CI/test results when evaluating the current code, rather than assuming
that a checked-in report covers every later revision.

## Demo and scope

[Demo guide](docs/demo-script.md). The authored page in `judge-dashboard/index.html`
is a scripted walkthrough of recorded evidence; it does not run agents or tests.
Serve it with `python -m http.server 8080 --directory judge-dashboard`.

This is a local workflow demonstration, not an enterprise deployment. The to-do
API deliberately omits authentication and production infrastructure. It was
built by a five-person team for the IBM Bob multi-agent problem statement.
