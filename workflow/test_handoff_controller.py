import json

from workflow.handoff_controller import create_handoff, find_gate, write_status


def _write(root, relative_path, content):
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_review_to_testing_requires_approved_review(tmp_path):
    gate = find_gate("review", "testing")
    assert gate is not None
    _write(tmp_path, "review_report.md", "## Verdict: CHANGES REQUESTED")

    try:
        create_handoff(tmp_path, gate, "Asha")
    except ValueError as error:
        assert str(error) == "Review report is not APPROVED"
    else:
        raise AssertionError("an unapproved review must block the hand-off")


def test_testing_to_docs_creates_auditable_handoff(tmp_path):
    gate = find_gate("testing", "docs")
    assert gate is not None
    _write(tmp_path, "test_report.md", "| Failed | 0 |\n**PASS — ready to merge.**")

    log, record = create_handoff(tmp_path, gate, "Asha")

    assert record["target"] == "docs"
    assert record["approved_by"] == "Asha"
    saved = json.loads(log.read_text(encoding="utf-8"))
    assert saved["bob_mode"] == "Pitch/Docs Agent"


def test_status_snapshot_contains_all_stages(tmp_path):
    _write(tmp_path, "design_brief.md", "brief")
    _write(tmp_path, "app/main.py", "app")
    _write(tmp_path, "review_report.md", "## Verdict: APPROVED")
    _write(tmp_path, "test_report.md", "| Failed | 0 |\n**PASS — ready to merge.**")
    _write(tmp_path, "debug_report.md", "diagnosis")
    _write(tmp_path, "docs/demo-script.md", "demo")

    status = write_status(tmp_path)

    content = status.read_text(encoding="utf-8")
    assert "| Research | READY" in content
    assert "| Docs | READY" in content
