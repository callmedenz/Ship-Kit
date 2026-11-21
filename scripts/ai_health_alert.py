import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

try:
    from .gmail_alert import send_gmail
except ImportError:
    from gmail_alert import send_gmail


load_dotenv()


def check_service(name, url):
    if not url:
        return {
            "name": name,
            "status": "not_configured",
            "detail": "No public health URL configured.",
        }

    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ShipKit-Health-Monitor/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            return {
                "name": name,
                "status": "healthy" if response.status < 400 else "broken",
                "http_status": response.status,
            }
    except urllib.error.HTTPError as error:
        return {"name": name, "status": "broken", "http_status": error.code}
    except Exception as error:
        return {"name": name, "status": "broken", "detail": str(error)}


def fallback_message(results):
    broken = [result for result in results if result["status"] == "broken"]
    not_configured = [result for result in results if result["status"] == "not_configured"]

    if broken:
        names = ", ".join(result["name"] for result in broken)
        return f"ALERT: ShipKit health check failed for {names}. Immediate review required."

    if not_configured:
        names = ", ".join(result["name"] for result in not_configured)
        return f"ShipKit health check: monitored services are healthy. Not configured: {names}."

    return "ShipKit health check: all monitored services are running normally."


def generate_gemini_message(api_key, model, results):
    prompt = f"""
Write a short email status message for this DevSecOps health check.
Rules:
- Return only valid JSON.
- Use exactly one key: "message".
- Keep the message under 1900 characters.
- If any service status is "broken", start with "ALERT:" and describe a serious issue.
- If every configured service is healthy, report that operations are normal.
- Do not invent services, URLs, metrics, or causes.

Health results:
{json.dumps(results, indent=2)}
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
    message = json.loads(text).get("message", "")
    return str(message).strip()[:1900]


def main():
    results = [
        check_service("ShipKit", os.environ.get("SHIPKIT_HEALTH_URL")),
        check_service("Prometheus", os.environ.get("PROMETHEUS_HEALTH_URL")),
        check_service("Grafana", os.environ.get("GRAFANA_HEALTH_URL")),
    ]

    fallback = fallback_message(results)
    api_key = os.environ.get("GEMINI_API_KEY")
    message = fallback
    if api_key:
        try:
            message = generate_gemini_message(
                api_key,
                os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                results,
            ) or fallback
        except Exception as error:
            print(f"Gemini health message failed: {error}")

    print(json.dumps(results, indent=2))
    print(message)

    send_gmail("ShipKit AI Health Alert", message)


if __name__ == "__main__":
    main()
