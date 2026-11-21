import argparse
import json
import os
import sys
import urllib.request
from pathlib import PurePosixPath

from dotenv import load_dotenv

try:
    from .gmail_alert import send_gmail
except ImportError:
    from gmail_alert import send_gmail


load_dotenv()


ALLOWED_FILES = {
    "Dockerfile",
    "requirements.txt",
    "k8s/deployment.yaml",
}


def extract_vulnerabilities(trivy_report):
    findings = []
    for report in trivy_report.get("Results", []):
        for vulnerability in report.get("Vulnerabilities", []) or []:
            severity = vulnerability.get("Severity", "")
            if severity not in {"CRITICAL", "HIGH"}:
                continue
            findings.append({
                "package": vulnerability.get("PkgName"),
                "installed_version": vulnerability.get("InstalledVersion"),
                "fixed_version": vulnerability.get("FixedVersion"),
                "vulnerability_id": vulnerability.get("VulnerabilityID"),
                "severity": severity,
                "title": vulnerability.get("Title"),
            })
    return findings


def safe_file_path(path):
    normalized = PurePosixPath(path)
    if normalized.is_absolute() or ".." in normalized.parts:
        return None
    value = normalized.as_posix()
    return value if value in ALLOWED_FILES else None


def call_gemini(api_key, model, findings):
    prompt = f"""
You are a cautious DevSecOps assistant.
Analyze this Trivy JSON finding summary and propose secure fixes.

Rules:
- Return only a valid JSON object.
- Do not invent dependency versions or fixed versions.
- Prefer the fixed_version from each finding.
- Only edit these files: Dockerfile, requirements.txt, k8s/deployment.yaml.
- If no safe fix exists, return an empty files array.
- Each file entry must contain "path" and "content" containing the complete replacement file.
- Never include credentials or executable instructions.
- Include a short "summary" and an email-compatible "email_message".

Findings:
{json.dumps(findings, indent=2)}
"""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)

    text = result["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def apply_files(response, repository):
    applied = []
    for file_change in response.get("files", []):
        path = safe_file_path(file_change.get("path", ""))
        content = file_change.get("content")
        if path is None or not isinstance(content, str):
            continue
        destination = os.path.join(repository, *PurePosixPath(path).parts)
        with open(destination, "w", encoding="utf-8") as destination_file:
            destination_file.write(content)
        applied.append(path)
    return applied


def fallback_result(findings):
    count = len(findings)
    if count:
        summary = f"Trivy found {count} HIGH or CRITICAL vulnerability findings."
    else:
        summary = "No HIGH or CRITICAL Trivy findings were detected."
    return {
        "summary": summary,
        "email_message": f"ShipKit security scan: {summary}",
        "files": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trivy-json", required=True)
    parser.add_argument("--repository", default=".")
    parser.add_argument("--summary-output", required=True)
    parser.add_argument("--email-output", required=True)
    args = parser.parse_args()

    with open(args.trivy_json, "r", encoding="utf-8") as report_file:
        trivy_report = json.load(report_file)

    findings = extract_vulnerabilities(trivy_report)
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        try:
            response = call_gemini(
                api_key,
                os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                findings,
            )
        except Exception as error:
            print(f"Gemini request failed: {error}", file=sys.stderr)
            response = fallback_result(findings)
    else:
        response = fallback_result(findings)

    applied = apply_files(response, args.repository)
    summary = str(response.get("summary", "")).strip()
    email_message = str(response.get("email_message", "")).strip()
    if not summary:
        summary = fallback_result(findings)["summary"]
    if not email_message:
        email_message = fallback_result(findings)["email_message"]

    with open(args.summary_output, "w", encoding="utf-8") as summary_file:
        json.dump({"summary": summary, "applied_files": applied}, summary_file)
    with open(args.email_output, "w", encoding="utf-8") as email_file:
        email_file.write(email_message)

    print(summary)
    if applied:
        print("Applied AI-proposed files:", ", ".join(applied))
    send_gmail("ShipKit Security Scan", email_message)


if __name__ == "__main__":
    main()
