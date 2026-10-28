"""Records the real result of every executed test into test-results.json."""
import json

RESULTS = []


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.failed):
        RESULTS.append({
            "name": report.nodeid,
            "result": "passed" if report.passed else "failed",
            "failure_message": report.longreprtext if report.failed else None,
        })


def pytest_sessionfinish(session, exitstatus):
    with open("test-results.json", "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2)
