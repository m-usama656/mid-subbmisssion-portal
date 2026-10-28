"""Builds the final test report and POSTs it to the local receiver (via tunnel)."""
import datetime
import json
import os
import sys
import time
import urllib.request


def build_report():
    results = []
    if os.path.exists("test-results.json"):
        with open("test-results.json", encoding="utf-8") as f:
            results = json.load(f)

    passed = sum(r["result"] == "passed" for r in results)
    failed = sum(r["result"] == "failed" for r in results)

    return {
        "repository": os.getenv("GITHUB_REPOSITORY", "local"),
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "pipeline_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tests": results,
        "summary": {"total": len(results), "passed": passed, "failed": failed},
        "overall_status": "passed" if results and failed == 0 else "failed",
    }


def write_local_copies(report):
    """Files used by the optional email step."""
    with open("test-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    s = report["summary"]
    lines = [
        f"Repository: {report['repository']}",
        f"Branch: {report['branch']}",
        f"Commit: {report['commit_sha']}",
        f"Result: {report['overall_status'].upper()}",
        f"Total: {s['total']}  Passed: {s['passed']}  Failed: {s['failed']}",
        "",
    ]
    lines += [f"- {t['name']}: {t['result']}" for t in report["tests"]]
    with open("email-body.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    report = build_report()
    write_local_copies(report)

    url = os.environ.get("RECEIVER_URL", "").strip()
    if not url:
        print("RECEIVER_URL is not set; add it as a repository secret.")
        sys.exit(1)

    data = json.dumps(report).encode("utf-8")
    headers = {"Content-Type": "application/json", "ngrok-skip-browser-warning": "1"}
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                print("Receiver replied:", resp.status)
                return
        except Exception as e:  # noqa: BLE001
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(3)
    sys.exit(1)


if __name__ == "__main__":
    main()
