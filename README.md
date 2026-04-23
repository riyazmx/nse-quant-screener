# NSE Quant Screener

Production-grade NSE stock screener built in strict implementation phases.

## Phase 1 (Scaffold)

This phase sets up a runnable project skeleton with:

- Repository layout for config, data, outputs, source modules, and tests.
- Importable placeholder loaders for universe, prices, fundamentals, and metadata.
- Config loading from `config/settings.yaml`.
- Application logging.
- A runnable `main.py` entrypoint.

## Project Structure

```text
config/
  settings.yaml
data/
  raw/
  processed/
  cache/
outputs/
  reports/
  charts/
  tables/
src/
  cleaning/
  loaders/
  utils/
tests/
main.py
requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Expected behavior in Phase 1:

- App starts successfully.
- Config is read from `config/settings.yaml`.
- Placeholder loaders execute and log row counts.

## Notes

- Quant logic definitions are intentionally untouched in this scaffold phase.
- No notebooks are used.
- Paths are handled with `pathlib`.
