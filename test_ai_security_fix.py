import json
import tempfile
from scripts.ai_security_fix import apply_files, extract_vulnerabilities, safe_file_path
from scripts.ai_health_alert import fallback_message
from scripts.gmail_alert import send_gmail


def test_extracts_only_high_and_critical_findings():
    report = {
        "Results": [{
            "Vulnerabilities": [
                {"VulnerabilityID": "CVE-1", "Severity": "HIGH", "PkgName": "openssl"},
                {"VulnerabilityID": "CVE-2", "Severity": "LOW", "PkgName": "curl"},
            ],
        }],
    }

    findings = extract_vulnerabilities(report)

    assert [finding["vulnerability_id"] for finding in findings] == ["CVE-1"]


def test_rejects_paths_outside_allowed_files():
    assert safe_file_path("../../.github/workflows/ci-cd.yml") is None
    assert safe_file_path("/tmp/Dockerfile") is None
    assert safe_file_path("Dockerfile") == "Dockerfile"


def test_applies_complete_replacement_to_allowed_file():
    with tempfile.TemporaryDirectory() as directory:
        open(f"{directory}/requirements.txt", "w", encoding="utf-8").write("old-package\n")

        applied = apply_files(
            {
                "files": [{
                    "path": "requirements.txt",
                    "content": "old-package==2.0\n",
                }],
            },
            directory,
        )

        assert applied == ["requirements.txt"]
        assert open(f"{directory}/requirements.txt", encoding="utf-8").read() == "old-package==2.0\n"


def test_health_fallback_reports_service_failure():
    message = fallback_message([
        {"name": "ShipKit", "status": "broken", "http_status": 503},
        {"name": "Prometheus", "status": "healthy", "http_status": 200},
    ])

    assert message.startswith("ALERT:")
    assert "ShipKit" in message


def test_health_fallback_reports_normal_operations():
    message = fallback_message([
        {"name": "ShipKit", "status": "healthy", "http_status": 200},
        {"name": "Prometheus", "status": "healthy", "http_status": 200},
        {"name": "Grafana", "status": "healthy", "http_status": 200},
    ])

    assert "running normally" in message


def test_gmail_returns_safely_when_not_configured(monkeypatch):
    monkeypatch.delenv("GMAIL_SENDER", raising=False)
    monkeypatch.delenv("GMAIL_RECIPIENT", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)

    assert send_gmail("Test", "Test body") is False
