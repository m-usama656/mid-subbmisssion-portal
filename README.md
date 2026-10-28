# Assignment Submission Portal (CSC418 DevOps Lab Midterm)

A small Flask web app where students submit their name, registration number,
assignment title and a submission URL. Every push to GitHub is tested
automatically; the test report is sent to a receiver on my own computer, which
saves it as `test-report.json`.

## Project layout

| Path | Purpose |
|------|---------|
| `app.py`, `templates/` | The portal (validation, saving, listing) |
| `tests/test_app.py` | Automated tests (3 required cases) |
| `conftest.py` | Records real test results to `test-results.json` |
| `scripts/send_report.py` | Builds the report and POSTs it to the receiver |
| `receiver/receiver.py` | Local HTTP receiver, saves `test-report.json` |
| `.github/workflows/ci.yml` | CI pipeline (tests, report, optional email, optional Pages deploy) |
| `docs/index.html` | Static demo published to GitHub Pages (bonus) |

## 1. Run the application

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Submissions are stored in `submissions.json`.

## 2. Run the tests

```bash
pytest -v
```
Tests: valid submission saved and listed; missing registration number rejected;
invalid URL rejected and not saved.

## 3. Start the receiver (needed for CI reports)

Terminal 1 - the receiver (listens on http://127.0.0.1:5001/report):
```bash
python receiver/receiver.py
```
Terminal 2 - a tunnel so GitHub can reach this computer (ngrok free static domain):
```bash
ngrok config add-authtoken <YOUR_TOKEN>
ngrok http --url=<your-domain>.ngrok-free.app 5001
```
Add a GitHub repository secret (Settings > Secrets and variables > Actions):

* `RECEIVER_URL` = `https://<your-domain>.ngrok-free.app/report`

Keep both terminals running while you push. After each push the pipeline runs
the tests and the receiver writes the fresh `test-report.json` in the folder
where the receiver was started.

Local check without GitHub:
```bash
pytest -v
set RECEIVER_URL=http://127.0.0.1:5001/report      # Mac/Linux: export RECEIVER_URL=...
python scripts/send_report.py
```

## 4. CI pipeline

`.github/workflows/ci.yml` runs on every push: install, `pytest -v` (a failing test
fails the job), then `send_report.py` with `if: always()` so passing and failing
runs both deliver a report.

## 5. Bonus: GitHub Pages (conditional deploy)

1. Settings > Pages > Source: **GitHub Actions**.
2. Settings > Secrets and variables > Actions > Variables: create `ENABLE_PAGES` = `true`.
3. Push to `main`. The `deploy` job has `needs: test`, so it only runs when all tests
   pass; a failing run leaves the previous version unchanged.

Deployed URL: `https://<username>.github.io/<repo-name>/`

## 6. Bonus: email report

Add secrets `MAIL_USERNAME` (Gmail address), `MAIL_PASSWORD` (Gmail App Password),
`MAIL_TO` (recipient). The email step runs after every test run (pass or fail) and
contains commit, overall result, counts, each test result, and the JSON as attachment.
Without `MAIL_TO` the step is skipped.

## 7. Demo script

1. Push a harmless change: green run, `test-report.json` shows `"overall_status": "passed"`.
2. In `app.py`, make `is_valid_url` return `True`; push: red run, JSON shows `"failed"` with the failure message.
3. Restore `is_valid_url`; push: green run again, JSON shows `"passed"`.
