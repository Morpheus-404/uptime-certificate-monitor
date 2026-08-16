# Uptime Certificate Monitor

A lightweight uptime and SSL certificate monitoring tool built with **Python**, **Docker**, and **Kubernetes**.

This project is part of my software engineering portfolio. It focuses on clean architecture, modern Python packaging, automated testing, and containerized deployment while solving a practical monitoring problem.

The application periodically checks a list of websites, verifies their availability, inspects SSL certificate expiration dates, and reports potential issues.
The primary goal of this project is to demonstrate practical DevOps and software engineering skills through a clean, production-inspired architecture.


---

# Features

## Implemented

* HTTP/HTTPS availability checks
* SSL certificate expiration monitoring
* Configurable URL list
* Configurable request timeout
* Configurable SSL warning threshold
* Discord webhook notifications
* Structured console logging
* Automated testing with Pytest
* Docker containerization
* Docker Compose support

## Planned

* Slack webhook notifications
* Kubernetes CronJob deployment
* Continuous Integration with GitHub Actions

---

# Tech Stack

* **Python 3.12+**
* **Docker**
* **Docker Compose**
* **Pytest**
* **PyYAML**

Planned:

* **Kubernetes (kind)**
* **GitHub Actions**
* **Ruff**

---

# Project Structure

```text
.
├── src/
│   └── monitor/        Application source code
├── tests/              Unit tests
├── config.yaml         Monitoring configuration
├── compose.yaml        Local container configuration
├── Dockerfile          Container image definition
├── .env.example        Environment variable template
└── pyproject.toml      Python project configuration
```

---

# Configuration

Monitoring targets and check settings are configured in `config.yaml`.

Discord notifications use the `DISCORD_WEBHOOK_URL` environment variable.

Create a local `.env` file based on `.env.example`:

```text
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

The `.env` file may contain secrets and must not be committed to version control.

---

# Running with Docker Compose

Build and run the monitor with:

```bash
docker compose run --rm monitor
```

Docker Compose:

* builds the application image
* mounts `config.yaml` into the container as read-only
* provides `DISCORD_WEBHOOK_URL` from the local environment configuration
* removes the container after the monitoring run completes

The application exits with:

* `0` if all monitoring checks succeed
* `1` if one or more checks fail

---

# Development

Install the project with development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

---

# Project Goals

This project is intended to demonstrate practical experience with:

* Python application development
* Clean project architecture
* Automated testing
* Docker containerization
* Kubernetes workloads
* Continuous Integration
* DevOps best practices

---

# License

This project is licensed under the **MIT License**.
