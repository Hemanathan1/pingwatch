"""
Security Tests
Checks: SSL validity, HTTPS redirect enforcement, security headers, open port scanning.
"""

import socket
import requests
from requests.exceptions import SSLError, RequestException


def check_ssl_valid(url: str) -> dict:
    """Verify SSL certificate is valid (no SSL errors)."""
    try:
        resp = requests.get(url, timeout=10, verify=True)
        return {"pass": True, "detail": f"SSL valid — HTTP {resp.status_code}"}
    except SSLError as e:
        return {"pass": False, "detail": f"SSL error: {e}"}
    except RequestException as e:
        return {"pass": False, "detail": str(e)}


def check_https_redirect(host: str) -> dict:
    """Check that HTTP automatically redirects to HTTPS."""
    try:
        resp = requests.get(f"http://{host}", timeout=10, allow_redirects=True)
        if resp.url.startswith("https://"):
            return {"pass": True, "detail": f"Redirected to {resp.url}"}
        else:
            return {"pass": False, "detail": f"No HTTPS redirect — final URL: {resp.url}"}
    except RequestException as e:
        return {"pass": False, "detail": str(e)}


def check_hsts_header(url: str) -> dict:
    """Check for Strict-Transport-Security header."""
    try:
        resp = requests.get(url, timeout=10)
        hsts = resp.headers.get("Strict-Transport-Security")
        if hsts:
            return {"pass": True, "detail": f"HSTS: {hsts}"}
        else:
            return {"pass": False, "detail": "Strict-Transport-Security header missing"}
    except RequestException as e:
        return {"pass": False, "detail": str(e)}


def check_x_content_type(url: str) -> dict:
    """Check for X-Content-Type-Options header."""
    try:
        resp = requests.get(url, timeout=10)
        val = resp.headers.get("X-Content-Type-Options")
        if val:
            return {"pass": True, "detail": f"X-Content-Type-Options: {val}"}
        else:
            return {"pass": False, "detail": "X-Content-Type-Options header missing"}
    except RequestException as e:
        return {"pass": False, "detail": str(e)}


def port_scan(host: str, ports: list, timeout: float = 3) -> dict:
    """Scan a list of ports and report which are open."""
    open_ports = []
    closed_ports = []
    for port in ports:
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            open_ports.append(port)
        except Exception:
            closed_ports.append(port)
    detail = f"Open: {open_ports} | Closed/filtered: {closed_ports}"
    return {"pass": True, "detail": detail, "open_ports": open_ports}


def run_security_tests(suite_config: dict) -> list:
    results = []

    for test in suite_config.get("tests", []):
        name  = test["name"]
        check = test["check"]

        if check == "ssl_valid":
            r = check_ssl_valid(test["url"])
        elif check == "https_redirect":
            r = check_https_redirect(test["host"])
        elif check == "hsts_header":
            r = check_hsts_header(test["url"])
        elif check == "x_content_type":
            r = check_x_content_type(test["url"])
        elif check == "port_scan":
            r = port_scan(test["host"], test.get("ports", []), test.get("timeout", 3))
        else:
            r = {"pass": False, "detail": f"Unknown check type: {check}"}

        results.append({
            "name": name,
            "status": "PASS" if r["pass"] else "FAIL",
            "detail": r["detail"],
            "check_type": check,
        })

    return results
