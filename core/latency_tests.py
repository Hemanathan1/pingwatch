"""
Latency / Performance Tests
Measures ICMP ping latency and HTTP response time, checks against thresholds.
"""

import subprocess
import platform
import time
import re
import requests
from requests.exceptions import RequestException


def ping_host(host: str, count: int = 4) -> dict:
    """
    Run a system ping and parse avg latency.
    Works on Linux, macOS, and Windows.
    """
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(count), host]
        avg_pattern = r"Average = (\d+)ms"
    else:
        cmd = ["ping", "-c", str(count), host]
        avg_pattern = r"min/avg/max[^=]+=\s*[\d.]+/([\d.]+)/"

    try:
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        match = re.search(avg_pattern, output.stdout)
        if match:
            avg_ms = float(match.group(1))
            return {"reachable": True, "avg_ms": avg_ms, "error": None}
        else:
            return {"reachable": False, "avg_ms": None, "error": "Could not parse ping output"}
    except subprocess.TimeoutExpired:
        return {"reachable": False, "avg_ms": None, "error": "Ping command timed out"}
    except FileNotFoundError:
        return {"reachable": False, "avg_ms": None, "error": "ping not found on system"}


def http_response_time(url: str, timeout: float = 10) -> dict:
    """Measure HTTP GET response time in milliseconds."""
    start = time.time()
    try:
        resp = requests.get(url, timeout=timeout)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return {"success": True, "elapsed_ms": elapsed_ms, "status": resp.status_code}
    except RequestException as e:
        return {"success": False, "elapsed_ms": None, "error": str(e)}


def run_latency_tests(suite_config: dict) -> list:
    results = []

    for test in suite_config.get("tests", []):
        name = test["name"]

        # Ping-based test
        if "host" in test and "max_avg_ms" in test:
            count   = test.get("count", 4)
            max_ms  = test["max_avg_ms"]
            r       = ping_host(test["host"], count)

            if not r["reachable"]:
                status = "ERROR"
                detail = r["error"]
            elif r["avg_ms"] <= max_ms:
                status = "PASS"
                detail = f"Avg latency {r['avg_ms']}ms ≤ threshold {max_ms}ms"
            else:
                status = "FAIL"
                detail = f"Avg latency {r['avg_ms']}ms > threshold {max_ms}ms"

        # HTTP response time test
        elif "url" in test and "max_response_ms" in test:
            max_ms = test["max_response_ms"]
            r      = http_response_time(test["url"])

            if not r["success"]:
                status = "ERROR"
                detail = r.get("error", "Request failed")
            elif r["elapsed_ms"] <= max_ms:
                status = "PASS"
                detail = f"Response {r['elapsed_ms']}ms ≤ threshold {max_ms}ms"
            else:
                status = "FAIL"
                detail = f"Response {r['elapsed_ms']}ms > threshold {max_ms}ms"

        else:
            status = "ERROR"
            detail = "Invalid test config — need host+max_avg_ms or url+max_response_ms"

        results.append({"name": name, "status": status, "detail": detail})

    return results
