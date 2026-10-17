# Local deployment

This is a loopback-only educational application, not a production deployment guide.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`; API documentation is at `/docs`. Keep the terminal running. `make run` is a shortcut after installation. Reports and generated artifacts remain local under `data/`. The app can generate a missing model automatically for the normal local entry point, while `create_app(..., auto_train=False)` fails visibly when artifacts are unavailable for controlled tests.

Docker support is present in `Dockerfile` and CI, but Docker was not installed during the local audit. No public bind, cloud deployment, external authentication or banking integration is supported.
