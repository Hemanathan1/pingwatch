"""
HTTP / HTTPS Behaviour Tests
Validates status codes, response body content, content-type, and response timing.
"""

import time
import requests
from requests.exceptions import RequestException


def run_http_tests(suite_config: dict) -> list:
    results = []

    for test in suite_config.get("tests", []):
        name             = test["name"]
        url              = test["url"]
        expected_status  = test.get("expected_status", 200)
        expected_body    = test.get("expected_body_contains")
        expected_ctype   = test.get("expected_content_type")
        timeout          = test.get("timeout", 10)

        start = time.time()
        try:
            resp = requests.get(url, timeout=timeout, allow_redirects=True)
            elapsed_ms = round((time.time() - start) * 1000, 2)

            failures = []

            # 1. Status code check
            if resp.status_code != expected_status:
                failures.append(f"Status {resp.status_code} != expected {expected_status}")

            # 2. Body keyword check
            if expected_body and expected_body not in resp.text:
                failures.append(f"Body missing '{expected_body}'")

            # 3. Content-type check
            if expected_ctype:
                actual_ctype = resp.headers.get("Content-Type", "")
                if expected_ctype not in actual_ctype:
                    failures.append(f"Content-Type '{actual_ctype}' != expected '{expected_ctype}'")

            status = "PASS" if not failures else "FAIL"
            detail = f"{elapsed_ms}ms | HTTP {resp.status_code}" if not failures else " | ".join(failures)

        except requests.Timeout:
            status, detail, elapsed_ms = "FAIL", f"Timed out after {timeout}s", None
        except RequestException as e:
            status, detail, elapsed_ms = "ERROR", str(e), None

        results.append({
            "name": name,
            "status": status,
            "detail": detail,
            "url": url,
            "response_ms": elapsed_ms,
        })

    return results
