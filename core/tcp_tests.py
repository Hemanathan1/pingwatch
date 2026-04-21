"""
TCP Connectivity Tests
Checks whether a host:port is reachable using a raw socket connection.
"""

import socket
import time


def tcp_connect(host: str, port: int, timeout: float = 5) -> dict:
    """Attempt a TCP connection and return result dict."""
    start = time.time()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        elapsed = round((time.time() - start) * 1000, 2)
        return {"connected": True, "latency_ms": elapsed, "error": None}
    except socket.timeout:
        return {"connected": False, "latency_ms": None, "error": "Connection timed out"}
    except ConnectionRefusedError:
        return {"connected": False, "latency_ms": None, "error": "Connection refused"}
    except socket.gaierror as e:
        return {"connected": False, "latency_ms": None, "error": f"DNS resolution failed: {e}"}
    except Exception as e:
        return {"connected": False, "latency_ms": None, "error": str(e)}


def run_tcp_tests(suite_config: dict) -> list:
    results = []

    for test in suite_config.get("tests", []):
        name     = test["name"]
        host     = test["host"]
        port     = test["port"]
        timeout  = test.get("timeout", 5)
        expect_fail = test.get("expect_fail", False)

        conn = tcp_connect(host, port, timeout)
        connected = conn["connected"]

        # Determine pass/fail
        if expect_fail:
            # We EXPECT this to fail — pass if it did fail
            status = "PASS" if not connected else "FAIL"
            detail = f"Correctly unreachable (expected)" if not connected else f"Unexpectedly reachable — investigate!"
        else:
            status = "PASS" if connected else "FAIL"
            detail = f"Latency: {conn['latency_ms']}ms" if connected else conn["error"]

        results.append({
            "name": name,
            "status": status,
            "detail": detail,
            "host": host,
            "port": port,
            "latency_ms": conn["latency_ms"],
        })

    return results
