param(
  [string]$FeatureRequest = "Build the API defined in docs/scope.md",
  [int]$MaxRetries = 3
)

Write-Host "== Research Agent =="
bob agents run research-agent "$FeatureRequest. Read docs/scope.md and write design_brief.md."

Write-Host "== Coding Agent (initial implementation) =="
bob agents run coding-agent "Implement design_brief.md."

$attempt = 0
$done = $false

while (-not $done -and $attempt -lt $MaxRetries) {
  Write-Host "== Testing Agent (attempt $attempt) =="
  bob agents run testing-agent "Write and run tests per design_brief.md, output test_report.md."

  $report = Get-Content test_report.md -Raw
  if ($report -match "Overall verdict: PASS") {
    Write-Host "Tests passed. Pipeline complete."
    $done = $true
  } else {
    Write-Host "Tests failed, re-invoking Coding Agent."
    bob agents run coding-agent "Fix the failures in test_report.md."
    $attempt++
  }
}

if (-not $done) {
  Write-Host "Max retries hit without a passing test suite. Manual intervention needed."
}