# Setup & Run

Python 3.11+ is supported (verified with Python 3.12).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m settlement_dashboard.pipeline
pytest
```

To rebuild the dashboard snapshot after a pipeline run:

```powershell
python scripts/build_dashboard_snapshot.py
```

The authored dashboard has already been built under `dashboard_app/dist`. To serve it locally:

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory dashboard_app/dist
```

Then open `http://127.0.0.1:4173/`. Do not open the HTML with `file://`; the split build loads its content-addressed JSON sidecar over HTTP.

