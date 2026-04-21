# 🔍 NetTest — Network Test Automation Framework

A Python-based CLI framework for automated network health validation.
Tests TCP connectivity, HTTP behaviour, security headers, and latency — all driven by a single YAML config file.

Built as a portfolio project demonstrating skills relevant to **Network QA / Test Engineering** roles (Cisco SD-WAN).

---

## 📁 Project Structure

```
nettest/
├── runner.py              # Main CLI entry point
├── test_config.yaml       # All test definitions (data-driven)
├── requirements.txt
├── core/
│   ├── tcp_tests.py       # TCP socket connectivity checks
│   ├── http_tests.py      # HTTP status, body, content-type validation
│   ├── security_tests.py  # SSL, HTTPS redirect, header & port scan checks
│   └── latency_tests.py   # Ping latency + HTTP response time
└── reports/
    └── reporter.py        # HTML + JSON report generator
```

---

## ⚡ Quick Start

```bash
# 1. Clone and install dependencies
git clone https://github.com/<your-username>/nettest
cd nettest
pip install -r requirements.txt

# 2. Run all test suites
python runner.py

# 3. Run a specific suite only
python runner.py --suite tcp http

# 4. Choose report format
python runner.py --format html
```

---

## 🧪 Test Suites

| Suite      | What it tests                                              |
|------------|------------------------------------------------------------|
| `tcp`      | TCP socket connectivity to host:port with timeout          |
| `http`     | HTTP status codes, body keywords, content-type headers     |
| `security` | SSL validity, HTTPS redirect, HSTS, X-Content-Type, port scan |
| `latency`  | ICMP ping avg latency + HTTP response time vs thresholds   |

---

## 📝 Adding a New Test Case

No Python changes needed. Just add a block to `test_config.yaml`:

```yaml
suites:
  http:
    tests:
      - name: "My API returns 200"
        url: "https://api.myservice.com/health"
        expected_status: 200
        timeout: 5
```

---

## 📊 Sample Output

```
==================================================
  Running suite: HTTP
==================================================
  ✅  [PASS ]  example.com returns HTTP 200              245ms | HTTP 200
  ✅  [PASS ]  Response contains expected keyword        251ms | HTTP 200
  ❌  [FAIL ]  Non-existent endpoint                     Status 404 != expected 200

  Summary: 2 passed, 1 failed, 0 errors  (1.4s)

📄 JSON report  → reports/report_20250410_143022.json
🌐 HTML report  → reports/report_20250410_143022.html
```

---

## 🔧 Tech Stack

- **Python 3.10+**
- `requests` — HTTP client
- `PyYAML` — config parsing
- `socket` / `subprocess` — TCP and ping primitives
- HTML report rendered with inline Jinja2-style templating

---

## 💡 Key Design Decisions

- **Data-driven tests**: All test cases live in YAML, not code — makes the framework easy to extend without touching Python
- **Modular suite runners**: Each protocol (TCP/HTTP/Security/Latency) is an independent module, easy to add new ones
- **Structured reporting**: Every run produces timestamped JSON + HTML reports, matching enterprise QA practices
- **`expect_fail` support**: Negative test cases are first-class — important for validating that bad configs are correctly rejected

---

## 📌 Relevance to Network QA / SD-WAN Testing

| Skill Area | How this project demonstrates it |
|---|---|
| Python automation | Entire framework written in Python |
| Test case design | 15+ structured cases across 4 suites |
| Networking (TCP/IP, HTTP) | TCP socket tests, HTTP validation, protocol checks |
| Security principles | SSL, HTTPS enforcement, header validation, port scanning |
| Debugging & reporting | Structured JSON/HTML reports with pass/fail detail |
| YAML-driven config | Separates test logic from test data |
