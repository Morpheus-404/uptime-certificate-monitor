# Uptime Certificate Monitor

A lightweight uptime and SSL certificate monitoring tool built with **Python**, **Docker**, and **GitHub Actions**.

The application monitors configured websites, checks their availability and SSL certificate expiration dates, and optionally sends Discord notifications when issues occur.

This project is part of my software engineering portfolio and demonstrates automated testing, containerization, scheduled execution, persistent logging, and CI/CD.

---

## Features

* HTTP/HTTPS availability checks
* SSL certificate expiration monitoring
* Configurable targets, timeouts, and warning thresholds
* Cron-based scheduled monitoring
* Optional Discord webhook notifications
* Console and persistent file logging
* UTC timestamps
* Automated tests with Pytest
* Code linting with Ruff
* Docker and Docker Compose support
* GitHub Actions CI
* Automated image publishing to GitHub Container Registry

---

## Tech Stack

**Python 3.12+ · Docker · Docker Compose · GitHub Actions · Pytest · Ruff · PyYAML · croniter**

---

## Configuration

Monitoring targets are configured in `config.yaml`:

```yaml
request_timeout_seconds: 10.0

checks:
  - type: http
    url: https://example.com

  - type: ssl
    hostname: example.com
```

Runtime settings are configured through a local `.env` file based on `.env.example`:

```dotenv
DISCORD_WEBHOOK_URL=your_discord_webhook_url
CRON_SCHEDULE=*/15 * * * *
```

Discord notifications are optional. `CRON_SCHEDULE` uses standard cron syntax and UTC. If it is not set, the scheduler defaults to every 15 minutes and logs a warning.

The `.env` file may contain secrets and must not be committed.

---

## Quick Start

### Scheduled monitoring with Docker Compose

Clone the repository, configure `config.yaml` and `.env`, then start the monitor:

```bash
docker compose up --build -d
```

Check its status:

```bash
docker compose ps
```

Follow the logs:

```bash
docker compose logs -f
```

Stop the monitor:

```bash
docker compose down
```

Monitoring results are also persisted in:

```text
logs/monitor.log
```

The log directory is mounted from the host and therefore survives container restarts.

### Single monitoring run

A prebuilt image is available from GitHub Container Registry:

```bash
docker pull ghcr.io/morpheus-404/uptime-certificate-monitor:latest
```

Linux / macOS:

```bash
docker run --rm \
  --mount type=bind,source="$(pwd)/config.yaml",target=/app/config.yaml,readonly \
  ghcr.io/morpheus-404/uptime-certificate-monitor:latest
```

Windows PowerShell:

```powershell
docker run --rm `
  --mount type=bind,source="${PWD}\config.yaml",target=/app/config.yaml,readonly `
  ghcr.io/morpheus-404/uptime-certificate-monitor:latest
```

A single run exits with code `0` when all checks succeed and `1` when one or more checks fail.

---

## Development

Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run quality checks:

```bash
ruff check .
pytest
```

Run locally:

```bash
python -m monitor.main
```

Or start the scheduler:

```bash
python -m monitor.scheduler
```

---

## CI/CD

GitHub Actions runs on pushes and pull requests targeting `master`.

The pipeline:

* runs Ruff
* runs the Pytest test suite
* validates the Docker build
* publishes `ghcr.io/morpheus-404/uptime-certificate-monitor:latest` on pushes to `master`

---

## Project Structure

```text
.
├── .github/workflows/   CI/CD
├── src/monitor/         Application source code
├── tests/               Unit tests
├── logs/                Persistent runtime logs
├── config.yaml          Monitoring configuration
├── compose.yaml         Docker Compose configuration
├── Dockerfile
└── pyproject.toml
```

---

## License

This project is licensed under the **MIT License**.
