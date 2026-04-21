"""
NetTest - Network Test Automation Framework
Main test runner: loads config, executes all test suites, generates report.
"""

import yaml
import time
import argparse
from datetime import datetime
from core.tcp_tests import run_tcp_tests
from core.http_tests import run_http_tests
from core.security_tests import run_security_tests
from core.latency_tests import run_latency_tests
from reports.reporter import generate_report


def load_config(path="test_config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def run_all(config, suite_filter=None):
    results = {
        "meta": {
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "started_at": datetime.now().isoformat(),
            "config_file": "test_config.yaml",
        },
        "suites": []
    }

    suite_runners = {
        "tcp":      run_tcp_tests,
        "http":     run_http_tests,
        "security": run_security_tests,
        "latency":  run_latency_tests,
    }

    for suite_name, runner_fn in suite_runners.items():
        if suite_filter and suite_name not in suite_filter:
            continue
        if suite_name not in config.get("suites", {}):
            continue

        print(f"\n{'='*50}")
        print(f"  Running suite: {suite_name.upper()}")
        print(f"{'='*50}")

        suite_start = time.time()
        suite_results = runner_fn(config["suites"][suite_name])
        suite_duration = round(time.time() - suite_start, 3)

        passed = sum(1 for r in suite_results if r["status"] == "PASS")
        failed = sum(1 for r in suite_results if r["status"] == "FAIL")
        errors = sum(1 for r in suite_results if r["status"] == "ERROR")

        results["suites"].append({
            "name": suite_name,
            "duration_s": suite_duration,
            "total": len(suite_results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "tests": suite_results,
        })

        for r in suite_results:
            icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⚠️")
            print(f"  {icon}  [{r['status']:5}]  {r['name']:<45}  {r.get('detail','')}")

        print(f"\n  Summary: {passed} passed, {failed} failed, {errors} errors  ({suite_duration}s)")

    results["meta"]["finished_at"] = datetime.now().isoformat()
    total_tests = sum(s["total"] for s in results["suites"])
    total_passed = sum(s["passed"] for s in results["suites"])
    total_failed = sum(s["failed"] for s in results["suites"])
    results["meta"]["total"] = total_tests
    results["meta"]["passed"] = total_passed
    results["meta"]["failed"] = total_failed

    return results


def main():
    parser = argparse.ArgumentParser(description="NetTest — Network Test Automation Framework")
    parser.add_argument("--config", default="test_config.yaml", help="Path to config file")
    parser.add_argument("--suite", nargs="*", choices=["tcp", "http", "security", "latency"],
                        help="Run specific suites only")
    parser.add_argument("--format", choices=["html", "json", "both"], default="both",
                        help="Output report format")
    args = parser.parse_args()

    print("\n🔍 NetTest — Network Test Automation Framework")
    print(f"   Config : {args.config}")
    print(f"   Suites : {args.suite or 'all'}")
    print(f"   Format : {args.format}")

    config = load_config(args.config)
    results = run_all(config, suite_filter=args.suite)
    generate_report(results, fmt=args.format)

    print(f"\n{'='*50}")
    print(f"  FINAL: {results['meta']['passed']}/{results['meta']['total']} tests passed")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
